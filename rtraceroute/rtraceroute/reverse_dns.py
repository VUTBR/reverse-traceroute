import requests


class ReverseDNS:
    def __init__(self, ip_address):
        self.request_url = 'https://stat.ripe.net/data/reverse-dns/data.json?resource='
        self.ip_address = ip_address
        self.domain = None

    @staticmethod
    def parse(response):
        domain = None
        try:
            delegations = response['data']['delegations']
            for delegation in delegations:
                for value in delegation:
                    if value['key'] == 'domain':
                        domain = value['value']
        except KeyError:
            pass  # domain not resolved

        return domain

    def run(self):
        response = requests.get(self.request_url + self.ip_address)
        self.domain = ReverseDNS.parse(response.json())
