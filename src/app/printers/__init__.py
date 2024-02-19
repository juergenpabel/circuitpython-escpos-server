class Printer:
    debug: bool = False

    def __init__(self, debug: bool):
        self.debug = debug

    def setup(self, config: toml.Dotty) -> bool:
        return True

    def loop(self) -> bool:
        return True

    def write(self, data: bytearray) -> None:
        pass


