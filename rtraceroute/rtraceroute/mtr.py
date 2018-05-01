from threading import Thread
import shell
import socket


class MtrException(Exception):
    pass


class Mtr(Thread):
    def __init__(self, distant_host, options=None, protocol='ICMP'):
        self.distant_host = socket.gethostbyname(distant_host)
        self.protocol = protocol
        self.options = ["--report", "--csv", "--aslookup", "--mpls", "--show-ips"]
        self.output = None
        self.errors = None
        super(Mtr, self).__init__()

    def _create_shell_command(self):
        return '{} {} {}'.format(
            'mtr',
            self.distant_host,
            ' '.join(self.options)
        )

    def create_measurement(self):
        mtr = shell.shell(self._create_shell_command())
        return mtr.output(), mtr.errors()

    def run(self):
        output, errors = self.create_measurement()
        self.output = output
        self.errors = errors
