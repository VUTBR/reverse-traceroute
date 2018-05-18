from ipwhois.net import Net
from ipwhois.asn import IPASN
import socket
import warnings


class Whois(object):

    def __init__(self, address):
        self.address = address
        self.result = self.run()

    def run(self):
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning)
                net = Net(socket.gethostbyname(self.address))
                obj = IPASN(net)
                results = obj.lookup()
        except:
            results = None
        return results

    def get_asn(self):
        if self.result is not None and self.result['asn'] != 'NA':
            if 'AS' not in self.result['asn']:
                return 'AS' + self.result['asn']
            else:
                return self.result['asn']
        return 'AS???'

    def get_country(self):
        if self.result is not None:
            return self.result['asn_country_code']
        return ''

    def get_asn_registry(self):
        if self.result is not None:
            return self.result['asn_registry']
        return ''
