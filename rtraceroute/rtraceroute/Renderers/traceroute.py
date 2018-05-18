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
                        except socket.error:
                            hostname = ip

                        rtt = 'NA'
                        if 'rtt' in response:
                            rtt = response['rtt']

                        mpls_label = ''
                        if 'icmpext' in response:
                            mpls_label = TracerouteRenderer.parse_mpls_label(response['icmpext'])

                        if ip not in [x.ip for x in hop_responses]:
                            asn = Whois(ip).get_asn()
                            rdns = ReverseDNS(ip_address=ip)
                            rdns.run()
                            hop_responses.append(Hop(hop_number, ip, hostname, asn, rtt,
                                                     domain=rdns.domain, packet_numbers=[response_position],
                                                     mpls_label=mpls_label))
                    else:
                        new_hop = Hop(hop_number, ip='*', hostname='*', asn='AS???', packet_numbers=[response_position])
                        if not new_hop in hop_responses:
                            hop_responses.append(new_hop)
                    response_position += 1

                hop_lines.append(hop_responses)
        return hop_lines


    @staticmethod
    def parse_mpls_label(imcp_ext):
        mpls_label = ''
        if 'obj' in imcp_ext and len(imcp_ext['obj']) > 0:
            obj = imcp_ext['obj'][0]
            if 'mpls' in obj:
                mpls_label = 'MPLS Label {} TTL={}'.format(
                    obj['mpls'][0]['label'],
                    obj['mpls'][0]['ttl']
                )
        return mpls_label
