#!/usr/bin/env python2

from config import *
from graph_visualizer import GraphVisualizer
from ip import IP
from mtr import Mtr
from paris_traceroute import ParisTraceroute
from path_comparator import PathComparator
from probe_selector import ProbeSelector
from Renderers.mtr import MtrRenderer
from Renderers.paris_traceroute import ParisTracerouteRenderer
from Renderers.traceroute import TracerouteRenderer
from ripe.atlas.cousteau import (
  Traceroute,
  AtlasSource,
  AtlasCreateRequest,
  AtlasResultsRequest
)
from time import sleep
from whois import Whois
import click
from datetime import datetime, timedelta
import logging


logging.getLogger().setLevel(logging.INFO)


# For colored output
class ConsoleColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class RIPEException(Exception):
    pass


class ReverseTraceroute(object):

    def __init__(self, distant_host, local_host, probe_count, protocol, description, verbose):
        self.distant_host = distant_host
        self.local_host = local_host if local_host is not None else IP().ip
        self.protocol = protocol
        self.description = description
        self.verbose = verbose
        self.probe_count = probe_count
        whois = Whois(distant_host)
        ps = ProbeSelector(
            asn=whois.get_asn(),
            country_code=whois.get_country(),
            target=distant_host,
            probe_count=probe_count
        )
        self.probe_ids = [str(x['prb_id']) for x in ps.get_near_probes_results()]
        self.msm_id = None  # set when msm is created

    def create_measurement(self):
        traceroute = Traceroute(
            af=4,
            target=self.local_host,
            protocol=self.protocol.upper(),
            description=self.description,
            paris=32,
            timeout=4000,
            packets=4,
        )

        source = AtlasSource(
            type="probes",
            value=",".join(self.probe_ids),
            requested=len(self.probe_ids)
        )

        # add 1 second to ensure starttime in the request is not in the past
        atlas_request = AtlasCreateRequest(
            key=ATLAS_API_KEY,
            measurements=[traceroute],
            sources=[source],
            is_oneoff=True,
            start_time=datetime.utcnow() + timedelta(seconds=1)
        )
        return atlas_request.create()

    def wait_for_all_results(self, msm_id, probe_count, limit=900):  # 15m timeout
        attempts = 0
        res = []
        while attempts < limit:
            res = self.get_result(msm_id)
            attempts += 1
            if len(res) == probe_count:
                break
            sleep(1)
        return res

    def get_result(self, msm_id):
        kwargs = {
            "msm_id": msm_id,
        }
        is_success, results = AtlasResultsRequest(**kwargs).create()
        return results

    def run(self):
        if self.verbose:
            logging.info('Gathering ripe probes.')

        is_success, response = self.create_measurement()

        if not is_success:
            raise RIPEException(response)

        if self.verbose:
            logging.info('Waiting for results.')
        msm = response["measurements"][0]
        self.msm_id = msm

        results = self.wait_for_all_results(msm_id=msm, probe_count=self.probe_count)
        return results


#                  #
#       MAIN       #
#                  #
@click.command()
@click.option(
    "--local-host", help="Host the RIPE traceroute is targeted to, defaults to this machine's address", required=False
)
@click.option(
    "--protocol", help="Protocol to use - ICMP, UDP, TCP, defaults to ICMP", required=False, default='ICMP'
)
@click.option(
    "--probe-count", help="Number of RIPE probes to request", required=False, default=1
)
@click.option(
    "--description", help="Measurement description", required=False, default="Reverse traceroute measurement"
)
@click.option(
    "-v", "--verbose", help="verbose output", count=True
)
@click.argument("distant-host")
def run(distant_host, local_host, protocol, probe_count, description, verbose):

    if verbose:
        logging.info(
            'running Paris-traceroute towards {}.'.format(distant_host)
        )
        logging.info(
            'Inferred local IP: {}.'.format(IP().ip)
        )

    forward_traceroute = ParisTraceroute(distant_host, protocol=protocol)
    forward_traceroute.start()

    if protocol.lower() != 'icmp':
        forward_icmp_traceroute = ParisTraceroute(distant_host, protocol='ICMP')
        forward_icmp_traceroute.start()

    rt = ReverseTraceroute(
        distant_host=distant_host,
        local_host=local_host,
        probe_count=probe_count,
        protocol=protocol,
        description=description,
        verbose=verbose
    )
    results = rt.run()

    forward_traceroute.join()

    if protocol.lower() != 'icmp':
        forward_icmp_traceroute.join()

    if forward_traceroute.errors:
        if verbose:
            logging.info(
                'Don\'t have root proviledges for paris-traceroute, '
                'using mtr instead. Consider running with sudo.'
            )
        print("Forward path:")
        forward_traceroute = Mtr(distant_host)
        forward_traceroute.start()
        forward_traceroute.join()
        parsed_ft_results = MtrRenderer.parse(forward_traceroute.output)
        MtrRenderer.render(parsed_ft_results)
    else:
        print("Forward path:")
        parsed_ft_results = ParisTracerouteRenderer.parse(
            forward_traceroute.output)
        if protocol.lower() != 'icmp':
            parsed_ft_icmp_results = ParisTracerouteRenderer.parse(
                forward_icmp_traceroute.output)
            #  if end of paths contains unknown host (*), try
            #  to complete the path to the destination using icmp
            parsed_ft_results = PathComparator.merge_paths(
                parsed_ft_results, parsed_ft_icmp_results)

        ParisTracerouteRenderer.render(parsed_ft_results)

    print("Return path:")
    parsed_rt_results = TracerouteRenderer.parse(results)
    TracerouteRenderer.render(parsed_rt_results)

    # print ASN Paths
    path_comparator = PathComparator(parsed_ft_results, parsed_rt_results)
    path_comparator.print_asn_paths()

    asn_symmetrical = path_comparator.compare_paths_by_asns()
    if asn_symmetrical:
        print('\n{}ASN paths appear to be symmetrical.{}'.format(
            ConsoleColors.OKGREEN,
            ConsoleColors.ENDC
        ))
    else:
        print('\n{}ASN paths appear NOT to be symmetrical.{}'.format(
            ConsoleColors.WARNING,
            ConsoleColors.ENDC
        ))

    # print Hostname paths
    path_comparator.print_hostname_paths()
    hostname_symmetrical = path_comparator.compare_paths_by_hostnames()
    if hostname_symmetrical:
        print('\n{}Hostname paths appear to be symmetrical.{}'.format(
            ConsoleColors.OKGREEN,
            ConsoleColors.ENDC))
    else:
        print('\n{}Hostname paths appear NOT to be symmetrical.{}'.format(
            ConsoleColors.WARNING,
            ConsoleColors.ENDC))

    ft_individual_paths = path_comparator.extract_individual_paths(
        parsed_ft_results)

    gv = GraphVisualizer(ft_individual_paths)
    gv.create_nxgraph()

    gv.highlight_return_path(return_path=parsed_rt_results)
    gv.save(name=distant_host)


if __name__ == '__main__':
    run()
