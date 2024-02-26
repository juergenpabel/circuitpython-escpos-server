import adafruit_logging as logging

from .handler import LogHandler
from app.printers import Printer, NullPrinter

class PrinterHandler(LogHandler):
    name: str = None
    printer: Printer = None
    server = None

    def __init__(self, server, name: str):
        LogHandler.__init__(self, False)
        self.server = server
        self.name = name
        self.printer = None

    def emit(self, record: logging._LogRecord) -> None:
        if self.isOffline():
            if self.server is not None:
                self.printer = self.server.getPrinter(self.name)
            if self.printer is None:
                LogHandler.emit(self, record)
            else:
                self.setOnline()
                if isinstance(self.printer, NullPrinter):
                    self.server.getLogger().warning(f"LOG_PRINTER='{self.name}' (in settings.toml) is not an (active) printer, log events will not be printed")
        if self.isOnline():
            self.printer.write(record.msg.encode())
   
