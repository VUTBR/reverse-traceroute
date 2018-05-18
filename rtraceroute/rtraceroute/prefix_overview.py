import requests


class PrefixOverview(object):

    def __init__(self, ip_address):
        self.request_url = 'https://stat.ripe.net/data/prefix-overview/data.json?max_related=50&resource='
        self.ip_address = ip_address
        self.prefix = None

    @staticmethod
    def parse(response):
        resource = None
        try:
            resource = response['data']['resource']
        except KeyError:
            pass  # prefix not resolved

        return resource

    def run(self):
        response = requests.get(self.request_url + self.ip_address)
        self.prefix = PrefixOverview.parse(response.json())
