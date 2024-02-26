import board
import busio

from . import Printer


class PrinterSerial(Printer):
    uart: busio.UART = None
    pin_tx: str = ''
    pin_rx: str = ''
    baud: int = 9600
    bits: int = 8
    parity: str = 'none'
    stopbits: int = 1


    def __init__(self, name: str):
        Printer.__init__(self, name)

    def setup(self, config: dict) -> bool:
        Printer.setup(self, config)
        self.pin_tx = config.get('PIN_TX')
        if self.pin_tx not in board.__dict__:
            print(f"        ERROR: PIN_TX not a valid pin name")
            return False
        self.pin_rx = config.get('PIN_RX')
        if self.pin_rx not in board.__dict__:
            print(f"        ERROR: PIN_RX not a valid pin name")
            return False
        self.baud = int(config.get('SERIAL_BAUD', 9600))
        if self.baud <= 0:
            print(f"        ERROR: SERIAL_BITS not valid")
            return False
        self.bits = int(config.get('SERIAL_BITS', 8))
        if self.bits not in [5,67,8,9]:
            print(f"        ERROR: SERIAL_BITS not valid")
            return False
        self.parity = config.get('SERIAL_PARITY', 'none').lower()
        if self.parity not in ['none', 'even', 'odd']:
            print(f"        ERROR: SERIAL_PARITY not valid")
            return False
        self.stopbits = int(config.get('SERIAL_STOPBITS', 1))
        if self.stopbits not in [1,2]:
            print(f"        ERROR: SERIAL_STOPBITS not valid")
            return False
        parity = None
        if self.parity == 'even':
            parity = busio.Parity.EVEN
        if self.parity == 'odd':
            parity = busio.Parity.ODD
        print(f"        DEBUG: instantiating busio.UART(tx=board.{self.pin_tx}, rx=board.{self.pin_rx}, baudrate={self.baud}, bits={self.bits}, parity=busio.Parity.{self.parity.upper()}, stop={self.stopbits})")
        self.uart = busio.UART(board.__dict__.get(self.pin_tx), board.__dict__.get(self.pin_rx),
                               baudrate=self.baud, bits=self.bits, parity=parity, stop=self.stopbits)
        return True

    def loop(self) -> bool:
        return True

    def write(self, data: bytearray) -> None:
        if self.uart is not None:
            self.uart.write(data)

