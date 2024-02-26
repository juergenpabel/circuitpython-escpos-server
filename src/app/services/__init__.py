class Service:

    def __init__(self, name: str):
        self.name = name

    def setup(self, config: dict, printers: dict) -> bool:
        self.printers = printers
        return True

    def loop(self) -> bool:
        return True

