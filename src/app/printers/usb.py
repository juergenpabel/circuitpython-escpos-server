import board
import usb.core
import usb_host

from . import Printer


class PrinterUSB(Printer):
    usb_vid: str = None
    usb_pid: str = None
    device = None


    def __init__(self, debug: bool):
        Printer.__init__(self, debug)


    def setup(self, config: toml.Dotty) -> bool:
        Printer.setup(self, config)
        self.usb_vid = config.get('USB_VID')
        self.usb_pid = config.get('USB_PID')
        if self.usb_vid is None or self.usb_pid is None:
            print(f"        ERROR in configuration: missing USB_VID/USB_PID values, skipping")
            return False
        print(f"        Connecting to USB printer '{self.usb_vid}:{self.usb_pid}'...")
        usb_host.Port(board.GP26, board.GP27)
        usb.core.find() # dummy enumeration because on RP2040 first enumeration always fails
        self.device = usb.core.find(idVendor=self.usb_vid, idProduct=self.usb_pid)
        if self.device is None:
            print(f"        ...device '{self.usb_vid}:{self.usb_pid}' not found")
            return False
        print(f"        ...connected to {self.device.idVendor:04x}:{self.device.idProduct:04x} {self.device.manufacturer} / {self.device.product} (#{self.device.serial_number})")
        self.device.set_configuration()
        return True


    def loop(self) -> bool:
        return True


    def write(self, data: bytearray) -> None:
        if device is not None:
            device.write(1, data)

