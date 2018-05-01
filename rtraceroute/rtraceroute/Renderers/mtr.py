from base_renderer import BaseRenderer
from hop import Hop
from reverse_dns import ReverseDNS
import csv
import re


class MtrRenderer(BaseRenderer):

    @staticmethod
    def parse(results):
        rows = csv.DictReader(results)
        iter_rows = iter(rows)
        next(iter_rows)  # skip header

        re_ip = re.compile(r'(\d+\.\d+\.\d+\.\d+)')
        hop_lines = []

        for row in iter_rows:
            hop_line = []

            try:
                ip = re_ip.search(row['Ip']).group(1)
            except AttributeError:
                ip = '*'  # this means no response from router

            hostname = re.sub(r'\(\d+\.\d+\.\d+\.\d+\)', '', row['Ip']).rstrip()
            rdns = ReverseDNS(ip_address=ip)
            rdns.run()

            hop = Hop(
                row['Hop'],
                ip,
                hostname,
                row['Asn'],
                row['Avg'],
                rdns.domain if rdns.domain is not None else ''
            )

            hop_line.append(hop)
            hop_lines.append(hop_line)
        return hop_lines
