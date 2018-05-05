from base_renderer import BaseRenderer
from Renderers.hop import Hop
from reverse_dns import ReverseDNS
from whois import Whois
import socket


class TracerouteRenderer(BaseRenderer):

    @staticmethod
    def parse(results):
        hop_lines = []

        for result in results:
            hops = result['result']
            for hop in hops:
                hop_number = hop['hop']
                hop_responses =[]
                response_position = 0
                for response in hop['result']:
                    if 'from' in response:
                        ip = response['from']
                        try:
                            hostname = socket.gethostbyaddr(ip)[0]
                        except socket.error as e:
                            hostname = ''

                        if ip not in [x.ip for x in hop_responses]:
                            asn = Whois(ip).get_asn()
                            rdns = ReverseDNS(ip_address=ip)
                            rdns.run()
                            hop_responses.append(Hop(hop_number, ip, hostname, asn, response['rtt'], domain=rdns.domain, packet_numbers=[response_position]))
                    else:
                        hop = Hop(hop_number, '*', asn='AS???', packet_numbers=[response_position])
                        if not hop in hop_responses:
                            hop_responses.append(hop)

                    response_position += 1

                hop_lines.append(hop_responses)
        return hop_lines
