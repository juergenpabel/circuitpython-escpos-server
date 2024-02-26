import wifi
import socketpool

import adafruit_logging as logging
import usyslog
from .handler import LogHandler

class SyslogHandler(LogHandler):
    server_ipv4: str = None
    syslog_client: usyslog.UDPClient = None

    def __init__(self, server_ipv4: str):
        LogHandler.__init__(self, False)
        self.server_ipv4 = server_ipv4
        if wifi.radio.connected and wifi.radio.ipv4_address is not None:
            self.setOnline()

    def setOnline(self) -> None:
        if self.server_ipv4 is not None:
            self.syslog_client = usyslog.UDPClient(socketpool.SocketPool(wifi.radio), self.server_ipv4, 514)
            LogHandler.setOnline(self)

    def setOffline(self) -> None:
        self.syslog_client = None
        LogHandler.setOffline(self)

    def emit(self, record: _LogRecord) -> None:
        if wifi.radio.connected is False or wifi.radio.ipv4_address is None or self.server_ipv4 is None:
            if self.isOnline():
                self.setOffline()
        else:
            if self.isOffline():
                self.setOnline()
        if self.isOnline():
            self.syslog_client.log(record.levelno, f"{record.levelname:<8} - {record.msg}")
        else:
            LogHandler.emit(self, record)
    
