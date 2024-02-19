import binascii
import toml

class Printer:
    debug: bool = False
    escpos_init: bytearray = bytearray()
    escpos_fini: bytearray = bytearray()


    def __init__(self, debug: bool):
        self.debug = debug


    def setup(self, config: toml.Dotty) -> bool:
        if 'ESCPOS-INIT' not in config:
            config['ESCPOS-INIT'] = "1b401b6404" # reset & feed 4 lines
        if 'ESCPOS-FINI' not in config:
            config['ESCPOS-FINI'] = "1b64081b6d" # feed 8 lines & partial cut
        self.escpos_init = binascii.unhexlify(config['ESCPOS-INIT'])
        self.escpos_fini = binascii.unhexlify(config['ESCPOS-FINI'])
        return True


    def loop(self) -> bool:
        return True


    def write_init(self) -> None:
        self.write(self.escpos_init)


    def write(self, data: bytearray) -> None:
        pass


    def write_fini(self) -> None:
        self.write(self.escpos_fini)

