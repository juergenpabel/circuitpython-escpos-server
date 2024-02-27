import time
import wifi
import socketpool
from adafruit_httpserver import Server, Route, Request, POST

from . import Service
from app.util.log import Log

class ServiceHTTP(Service):
    http_server: Server = None

    def __init__(self, name: str):
        Service.__init__(self, name)

    def setup(self, config: dict, printers: dict) -> bool:
        Service.setup(self, config, printers)
        if 'SERVER_IPV4' not in config:
            config['SERVER_IPV4'] = '0.0.0.0'
        if 'SERVER_PORT' not in config:
            config['SERVER_PORT'] = 8080
        if 'SERVER_PATH' not in config:
            config['SERVER_PATH'] = '/'
        self.http_server = Server(socketpool.SocketPool(wifi.radio))
        self.http_server.add_routes([Route(config.get('SERVER_PATH'), POST, self._on_http_post_request)])
        self.http_server.start(config['SERVER_IPV4'], int(config['SERVER_PORT']))
        Log().getLogger(f"SERVICE:{self.name}").info(f"    ...HTTP server started")
        return True

    def loop(self) -> bool:
        if self.http_server is not None and self.http_server.port is not None:
            self.http_server.poll()
            return True
        return False

    def _on_http_post_request(self, request):
        Log().getLogger(f"SERVICE:{self.name}").debug(f"Processing HTTP request from IPv4='{request.client_address}' with body of {len(request.body)} bytes")
        for name, printer in self.printers:
            printer.write_init()
            for offset in range(0, len(request.body), 64):
                printer.write(request.body[offset:offset+64])
            printer.write_fini()

