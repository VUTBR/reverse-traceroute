from threading import Thread
import shell
import socket


class ParisTracerouteException(Exception):
    pass


class ParisTraceroute(Thread):

    def __init__(self, distant_host, options=None, protocol='ICMP'):
        self.distant_host = socket.gethostbyname(distant_host)
        self.protocol = protocol
        self.options = ["--algo=exhaustive", "-p " + protocol.lower()]
        self.output = None
        self.errors = None
        super(ParisTraceroute, self).__init__()

    def _create_shell_command(self):
        return '{} {} {}'.format(
            'paris-traceroute',
            ' '.join(self.options),
            self.distant_host
        )

    def create_measurement(self):
        pt = shell.shell(self._create_shell_command())
        return pt.output(), pt.errors()

    def run(self):
        output, errors = self.create_measurement()
        self.output = output
        self.errors = errors