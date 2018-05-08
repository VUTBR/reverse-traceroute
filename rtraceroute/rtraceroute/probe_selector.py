from config import ATLAS_API_KEY
from datetime import datetime
from asn_neighbours import AsnNeighbours
from ripe.atlas.cousteau import (
    AtlasSource,
    AtlasCreateRequest,
    AtlasResultsRequest,
    Ping,
)
from time import sleep
import logging


class ProbeSelector(object):

    def __init__(self, asn, target, country_code=None, probe_count=1):
        self.asn = asn
        self.country_code = country_code
        self.target = target
        self.probe_count = probe_count

    def get_asn_probe(self, asn):
        return AtlasSource(
            type='asn',
            value=asn,
            requested=self.probe_count
        )

    def get_local_area_probes(self):
        return AtlasSource(
            type='country',
            value=self.country_code,
            requested=5
        )

    def ping(self, source):
        ping = Ping(
            af=4,
            target=self.target,
            description="RTT measurement"
        )

        atlas_request = AtlasCreateRequest(
            start_time=datetime.utcnow(),
            key=ATLAS_API_KEY,
            measurements=[ping],
            sources=[source],
            is_oneoff=True
        )

        is_success, response = atlas_request.create()
        if not is_success:
            logging.warn(response)
            return []  # return empty list representing no results

        msm_id = response['measurements'][0]
        return self.wait_for_all_results(msm_id, source.requested)

    def get_near_probes_results(self):
        #  try to get responding probe from target ASN
        source = self.get_asn_probe(self.asn)
        results = self.ping(source)

        #  try to get responsing probe from neighbouring ASN
        if len(results) == 0:
            asn_neighbours = AsnNeighbours(self.asn)
            asn_neighbours.run()
            if asn_neighbours.neighbours is not None:
                for asn in asn_neighbours.neighbours:
                    source = self.get_asn_probe(asn)
                    results = self.ping(source)
                    if len(results) != 0:
                        return results

        #  if everything above fails, take few random probes from target country
        #  and choose one with the best rtt
        if len(results) == 0:
            source = self.get_local_area_probes()
            results = self.ping(source)
            results = sorted(results, key=lambda x: x['avg'])[:1]
        return results

    def wait_for_all_results(self, msm_id, probe_count, limit=900):
        """
        Waits for all Atlas probes to report collected data,
        when number of collected measurements equals number of Atlas probes
        required, results are returned

        :param msm_id: Measuremetn ID
        :param probe_count: number of probes required to create measurement
        :param limit: timeout
        :return: list of measurement results
        """
        attempts = 0
        old_res = []
        res = []
        while attempts < limit:
            res = self.get_result(msm_id)
            if old_res != res:
                attempts = 0
            else:
                attempts += 1
                if len(res) == probe_count:
                    break
            old_res = res
            sleep(1)
        return res

    @staticmethod
    def get_result(msm_id):
        kwargs = {
            "msm_id": msm_id,
        }
        is_success, results = AtlasResultsRequest(**kwargs).create()
        return results
