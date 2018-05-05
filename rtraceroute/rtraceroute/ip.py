from config import CHECKIP_SERVICE
from config import DNS_PORT
from config import GOOGLE_DNS
from config import LOCALHOST
import re
import socket
import urllib


class IP(object):
    def __init__(self):
        self.ip = self.get_ip()

    def get_ip(self):
        try:
            ip_addr = self.get_public_ip()
        except:
            ip_addr = self.get_local_ip()

        if not ip_addr:
            ip_addr = LOCALHOST
        return ip_addr

    @staticmethod
    def get_public_ip():
        data = str(urllib.urlopen(CHECKIP_SERVICE).read())
        public_ip = re.compile(r'(\d+\.\d+\.\d+\.\d+)').search(data).group(1)
        return public_ip

    @staticmethod
    def get_local_ip():
        all_local_ips = socket.gethostbyname_ex(socket.gethostname())[2]
        local_ips = []
        if not [ip for ip in all_local_ips if not ip.startswith("127")]:
            for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]:
                s.connect((GOOGLE_DNS, DNS_PORT))
                local_ips.append(s.getsockname()[0])
                s.close()
        return next(iter(local_ips or []), None)
