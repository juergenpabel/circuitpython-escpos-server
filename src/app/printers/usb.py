from microcontroller import Pin
import board
import usb.core
import usb_host

from . import Printer
from app.util.log import Log


class PrinterUSB(Printer):
    host_usb_dp: str = None
    host_usb_dm: str = None
    device_usb_vid: str = None
    device_usb_pid: str = None
    device = None

    def __init__(self, name: str, usb_dp: str, usb_dm: str):
        Printer.__init__(self, name)
        self.host_usb_dp = usb_dp
        self.host_usb_dm = usb_dm
        klass = self.__class__
        if not hasattr(klass, 'usb_host_port'):
            pin_usb_dp = board.__dict__.get(self.host_usb_dp)
            pin_usb_dm = board.__dict__.get(self.host_usb_dm)
            if isinstance(pin_usb_dp, Pin) is True and isinstance(pin_usb_dm, Pin) is True:
                klass.usb_host_port = usb_host.Port(pin_usb_dp, pin_usb_dm)

    def setup(self, config: dict) -> bool:
        if hasattr(self.__class__, 'usb_host_port') is False:
            Log().getLogger(f"PRINTER:{self.name}").error(f"        failed to instantiate usb_host.Port({self.host_usb_dp}, {self.host_usb_dm})")
            return False
        Printer.setup(self, config)
        self.device_usb_vid = config.get('USB_VID')
        self.device_usb_pid = config.get('USB_PID')
        if self.device_usb_vid is None or self.device_usb_pid is None:
            Log().getLogger(f"PRINTER:{self.name}").error(f"        missing USB_VID and/or USB_PID definitions")
            return False
        Log().getLogger(f"PRINTER:{self.name}").info(f"        Connecting to USB printer '{self.device_usb_vid}:{self.device_usb_pid}'...")
        usb.core.find() # dummy enumeration because on RP2040 first enumeration always fails
        self.device = usb.core.find(idVendor=self.device_usb_vid, idProduct=self.device_usb_pid)
        if self.device is None:
            Log().getLogger(f"PRINTER:{self.name}").warning(f"        ...device '{self.device_usb_vid}:{self.device_usb_pid}' not found")
            return False
        Log().getLogger(f"PRINTER:{self.name}").info(f"        ...connected to {self.device.idVendor:04x}:{self.device.idProduct:04x} {self.device.manufacturer} / {self.device.product} (#{self.device.serial_number})")
        self.device.set_configuration()
        return True

    def loop(self) -> bool:
        return True

    def write(self, data: bytearray) -> None:
        if self.device is not None:
            self.device.write(1, data)

