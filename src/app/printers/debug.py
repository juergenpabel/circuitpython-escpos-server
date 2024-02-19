from . import Printer

class PrinterDEBUG(Printer):

    def __init__(self):
        Printer.__init__(self, True)

    def setup(self, config: toml.Dotty) -> bool:
        return Printer.setup(self, config)

    def loop(self) -> bool:
        return True

    def write(self, data: bytearray) -> None:
        print(data)

