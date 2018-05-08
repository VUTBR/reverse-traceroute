import requests


class AsnNeighbours(object):
    def __init__(self, asn):
        self.request_url = 'https://stat.ripe.net/data/asn-neighbours/data.json?resource='
        self.asn = asn
        self.neighbours = None

    @staticmethod
    def parse(response):
        neighbours = None
        try:
            neighbours = response['data']['neighbours']
            #  sort list by 'power' (=number of as paths), in descending order
            neighbours.sort(key=lambda x: x['power'], reverse=True)
            return [str(x['asn']) for x in neighbours]
        except KeyError:
            pass  # no neighboring asns found
        return neighbours

    def run(self):
        response = requests.get(self.request_url + str(self.asn))
        self.neighbours = AsnNeighbours.parse(response.json())
