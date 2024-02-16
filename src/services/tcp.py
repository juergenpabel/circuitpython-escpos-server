import wifi
import socketpool

from . import Service


class ServiceTCP(Service):
    tcp_server:  socketpool.Socket = None
    client_timeout: int = 1
    printer = None


    def __init__(self, debug: bool):
        Service.__init__(self, debug)


    def setup(self, config: toml.Dotty, printer) -> bool:
        if 'SERVER_PORT' not in config:
            print("ERROR: Missing 'SERVER_PORT' config in table/secion 'SERVICE:TCP' in settings.toml, disabling service TCP")
            return False

        print(f"    Starting TCP server on IPv4='{config.get('SERVER_IPV4')}' and port '{config.get('SERVER_PORT')}'...")
        pool = socketpool.SocketPool(wifi.radio)
        self.tcp_server = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
        self.tcp_server.bind((config.get('SERVER_IPV4'), int(config.get('SERVER_PORT'))))
        self.tcp_server.listen(1)
        self.tcp_server.settimeout(0)
        self.client_timeout = int(config.get('CLIENT_TIMEOUT'))
        print(f"    ...TCP server now started")
        self.printer = printer
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
        if self.debug is True:
            print(f"Processing TCP connection from IPv4='{addr}'")
        if self.printer is not None:
            buffer = bytearray(64)
            self.printer.write(b'\x1b\x40')
            self.printer.write(b'\x1b\x64\x04')
            while sock is not None:
                count = sock.recv_into(buffer, len(buffer))
                self.printer.write(bytes(buffer[0:count]))
                if count < len(buffer):
                    sock = None
            self.printer.write(b'\x1b\x64\x08')
            self.printer.write(b'\x1b\x6d')

