from . import Printer

class PrinterDebug(Printer):

    def __init__(self, debug: bool):
        Printer.__init__(self, debug)

    def setup(self, config: toml.Dotty, printer) -> bool:
        return self.debug

    def loop(self) -> bool:
        return True

    def write(self, data: bytearray) -> None:
        print(data)

