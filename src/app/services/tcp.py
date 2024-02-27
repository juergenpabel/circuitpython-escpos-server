import wifi
import socketpool

from . import Service
from app.util.log import Log

class ServiceTCP(Service):
    tcp_server:  socketpool.Socket = None
    client_timeout: int = 1

    def __init__(self, name: str):
        Service.__init__(self, name)

    def setup(self, config: dict, printers: dict) -> bool:
        Service.setup(self, config, printers)
        if 'SERVER_IPV4' not in config:
            config['SERVER_IPV4'] = '0.0.0.0'
        if 'SERVER_PORT' not in config:
            config['SERVER_PORT'] = 9100
        if 'CLIENT_TIMEOUT' not in config:
            config['CLIENT_TIMEOUT'] = 3
        Log().getLogger(f"SERVICE:{self.name}").info(f"        Starting TCP server on IPv4='{config['SERVER_IPV4']}' and port '{config['SERVER_PORT']}'...")
        pool = socketpool.SocketPool(wifi.radio)
        self.tcp_server = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
        self.tcp_server.bind((config['SERVER_IPV4'], int(config['SERVER_PORT'])))
        self.tcp_server.listen(1)
        self.tcp_server.settimeout(0)
        self.client_timeout = int(config['CLIENT_TIMEOUT'])
        Log().getLogger(f"SERVICE:{self.name}").info(f"        ...TCP server now started")
        return True

    def loop(self) -> bool:
        if self.tcp_server is not None:
            try:
                sock, addr = self.tcp_server.accept()
                sock.settimeout(self.client_timeout)
                self._on_tcp_connect(sock, addr)
                sock.close()
            except OSError:
                pass
            return True
        return False

    def _on_tcp_connect(self, sock, addr):
        Log().getLogger(f"SERVICE:{self.name}").debug(f"    Processing TCP connection from IPv4='{addr}'")
        for printer in self.printers.values():
            printer.write_init()
        buffer = bytearray(64)
        while sock is not None:
            count = sock.recv_into(buffer, len(buffer))
            for printer in self.printers.values():
                printer.write(bytes(buffer[0:count]))
            if count < len(buffer):
                sock = None
        for printer in self.printers.values():
            printer.write_fini()

