import sys

from ripe.atlas.cousteau import AtlasStream
import logging


class ProbesLimitExceeded(Exception):
    pass


class Stream(object):

    def __init__(self, msm, probes_limit=None, type="result", channel="atlas_result", timeout=60):
        self.timeout = timeout
        self.msm = msm
        self.type = type
        self.channel = channel
        self.probes_limit = probes_limit
        self.probes_received = 0
        self.responses = []

    def stream(self):

        def on_result_response(result, *args):
            logging.warning("on_result_response fired")
            self.responses.append(result)
            self.probes_received += 1
            if self.probes_received >= self.probes_limit:
                print "Raise ProbesLimitExceeded()"
                raise ProbesLimitExceeded()

        stream = AtlasStream()
        stream.connect()
        stream.bind_channel(self.channel, on_result_response)

        try:
            stream.start_stream(stream_type=self.type, msm=self.msm)
            stream.timeout(self.timeout)
        except (KeyboardInterrupt, ProbesLimitExceeded) as e:
            stream.disconnect()

        return self.responses
