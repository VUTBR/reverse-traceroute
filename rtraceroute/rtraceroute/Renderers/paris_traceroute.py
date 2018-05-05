from base_renderer import BaseRenderer
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
                continue

            hop_number = re.search(r'\d+', current_line).group()
            current_line = re.sub(r'^\s*\d+\s+P\(\d+,\d+\)\s*', '', current_line)
            re_packet_numbers = re.compile(r':[\d+,]+')

            if not current_line:
                new_hop = Hop(hop_number, hostname='***', asn='AS???', packet_numbers=[])
                hop_line.append(new_hop)
                hop_lines.append(hop_line)
                continue

            hops = current_line.split(' ms ')
            for hop in hops:
                cur_hop = hop.split()

                if len(cur_hop) < 2:
                    continue

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

                new_hop = Hop(hop_number, ip, hostname, asn, domain=rdns.domain, packet_numbers=packet_numbers)
                hop_line.append(new_hop)

            hop_lines.append(hop_line)

        return hop_lines
