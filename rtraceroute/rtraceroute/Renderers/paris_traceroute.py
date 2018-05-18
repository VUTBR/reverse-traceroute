from base_renderer import BaseRenderer
from prefix_overview import PrefixOverview
from Renderers.hop import Hop
from reverse_dns import ReverseDNS
from whois import Whois
import re


class ParisTracerouteRenderer(BaseRenderer):

    @staticmethod
    def parse(results):
        re_ip = re.compile(r'(\d+\.\d+\.\d+\.\d+)')
        results = results[1:]

        hop_lines = []
        for line in results:
            hop_line = []
            current_line = line.replace(', ', ',')

            if 'MPLS Label' in current_line:
                # mpls labels is added to the hops in previous line
                # because this is how it is displayed in Paris traceroute output
                for hop in hop_lines[-1]:
                    hop.mpls_label = current_line.strip()
                continue

            hop_number = re.search(r'\d+', current_line).group()
            current_line = re.sub(r'^\s*\d+\s+P\(\d+,\d+\)\s*', '', current_line)
            re_packet_numbers = re.compile(r':[\d+,]+')

            if not current_line:
                new_hop = Hop(hop_number, hostname='*', asn='AS???', packet_numbers=[])
                hop_line.append(new_hop)
                hop_lines.append(hop_line)
                continue

            hops = current_line.split(' ms ')
            for hop in hops:
                cur_hop = hop.split()

                if len(cur_hop) < 2:
                    continue

                # get rid of !Tx tags
                while '!' in cur_hop[0]:
                    cur_hop = cur_hop[1:]

                hostname = cur_hop[0]

                ip = re_ip.search(hop).group(1)
                if not ip:
                    ip = '*'

                packet_numbers = re_packet_numbers.search(hop)
                if packet_numbers is not None:
                    packet_numbers = packet_numbers.group()
                    packet_numbers = packet_numbers.replace(':', '').split(',')
                    packet_numbers = map(int, packet_numbers)
                else:
                    packet_numbers = []

                asn = Whois(ip).get_asn()

                rdns = ReverseDNS(ip_address=ip)
                rdns.run()

                domain = rdns.domain
                if domain is None:
                    prefix = PrefixOverview(ip_address=ip)
                    prefix.run()
                    domain = prefix.prefix

                new_hop = Hop(hop_number, ip, hostname, asn, domain=domain, packet_numbers=packet_numbers)
                hop_line.append(new_hop)

            hop_lines.append(hop_line)
        return hop_lines
