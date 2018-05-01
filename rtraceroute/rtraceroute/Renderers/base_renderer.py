

class BaseRenderer(object):

    def __init__(self):
        pass

    @staticmethod
    def render(hop_lines):
        output = ''

        header = '{}  {}  {}\t\t{}\n'.format(
            'Hop',
            'Host',
            '(Asn)',
            'Avg RTT'
        )
        output += header

        for hop_line in hop_lines:
            hop_number = hop_line[0].hop_number
            hosts = []
            for hop in hop_line:
                hosts.append(
                    '{} {}{} ({}) {} {}'.format(
                        hop.hostname if hop.hostname else '*',
                        hop.ip if hop.ip != hop.hostname else '',
                        ':' + ','.join(map(str, hop.packet_numbers)) if hop.packet_numbers else '',
                        hop.asn if hop.asn else 'AS???',
                        str(hop.rtt) + ' ms' if hop.rtt else '',
                        '[{}]'.format(hop.domain) if hop.domain else ''
                    )
                )

            output += "{} {}\n".format(
                str(hop_number) + " " * (4 - len(str(hop_number))),
                ',\n     '.join(hosts)
            )
        print output
