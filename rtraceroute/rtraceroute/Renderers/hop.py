

class Hop(object):
    def __init__(self, hop_number, ip="", hostname="", asn="", rtt="", domain="", packet_numbers=list()):
        self.hop_number = hop_number
        self.ip = ip
        self.hostname = hostname
        self.asn = asn
        self.rtt = rtt
        self.domain = domain
        self.packet_numbers = packet_numbers

    def __eq__(self, other):
        return self.ip == other.ip and self.hop_number == other.hop_number
