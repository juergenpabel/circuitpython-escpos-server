
class Service:
    debug: bool = False

    def __init__(self, debug: bool):
        self.debug = debug

    def setup(self, config: toml.Dotty, printers: dict) -> bool:
        self.printers = printers
        return True

    def loop(self) -> bool:
        return True

