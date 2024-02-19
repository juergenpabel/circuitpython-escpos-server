import time
import wifi
import socketpool
from adafruit_httpserver import Server, Route, Request, POST

from . import Service


class ServiceHTTP(Service):
    http_server: Server = None


    def __init__(self, debug: bool):
        Service.__init__(self, debug)


    def setup(self, config: toml.Dotty, printers: dict) -> bool:
        Service.setup(self, config, printers)
        if 'SERVER_PATH' not in config:
            print("ERROR: Missing 'SERVER_PATH' config in table/secion 'SERVICE:HTTP' in settings.toml, disabling service HTTP")
            return False
        print(f"    Starting HTTP server on on IPv4='{config.get('SERVER_IPV4')}' and port={int(config.get('SERVER_PORT'))}...")
        self.http_server = Server(socketpool.SocketPool(wifi.radio), debug=self.debug)
        self.http_server.add_routes([Route(config.get('SERVER_PATH'), POST, self._on_http_post_request)])
        self.http_server.start(config.get('SERVER_IPV4'), int(config.get('SERVER_PORT')))
        print(f"    ...HTTP server started")
        return True


    def loop(self) -> bool:
        if self.http_server is not None and self.http_server.port is not None:
            self.http_server.poll()
            return True
        return False


    def _on_http_post_request(self, request):
        if self.debug is True:
            print(f"Processing HTTP request from IPv4='{request.client_address}' with body of {len(request.body)} bytes")
        for name, printer in self.printers:
            printer.write_init()
            for offset in range(0, len(request.body), 64):
                printer.write(request.body[offset:offset+64])
            printer.write_fini()

