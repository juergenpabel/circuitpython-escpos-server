import os
import time
import wifi

import toml
import adafruit_logging as logging
from .printers import Printer, NullPrinter
from .services import Service
from .util.log import Log


class Server(object):
    runtime: dict
    settings: toml.Dotty
    logger: logging.Logger

    def __new__(cls):
        if hasattr(cls, 'singleton') is False:
            cls.singleton = super(Server, cls).__new__(cls)
            cls.singleton.logger = Log().getLogger("root")
            cls.singleton.settings = None
            cls.singleton.runtime = { 'printers': {}, 'services': {} }
        return cls.singleton

    def getLogger(self) -> logging.Logger:
        return self.logger

    def getPrinter(self, name: str) -> Printer:
        if len(self.runtime['printers']) == 0:
            return None
        if name not in self.runtime['printers']:
            return NullPrinter()
        return self.runtime['printers'][name]

    def getService(self, name: str) -> Service:
        if name in self.runtime['services']:
            return self.runtime['services'][name]
        return None

    def setup(self):
        self.settings = toml.load('settings.toml')
        self.settings.setdefault('SYSTEM', {})
        self.settings.setdefault('ESCPOS', {'PRINTERS': {}, 'SERVICES': {}})
        self.settings.setdefault('PRINTER:DEBUG', {'DRIVER': 'DEBUG'})
        Log().setup(self, self.settings)
        self.logger.info(f"Configuring printers...")
        printers = dict()
        for printer_name in self.settings['ESCPOS']['PRINTERS']:
            self.logger.info(f"    Configuring printer '{printer_name}'...")
            printer_section = f"PRINTER:{printer_name}"
            if printer_section in self.settings and 'DRIVER' in self.settings[printer_section]:
                printer = None
                printer_driver = self.settings[printer_section]['DRIVER'].upper()
                if printer_driver == 'DEBUG':
                    from .printers.debug import PrinterDEBUG
                    printer = PrinterDEBUG()
                elif printer_driver == 'SERIAL':
                    from .printers.serial import PrinterSerial
                    printer = PrinterSerial()
                elif printer_driver == 'USB':
                    from .printers.usb import PrinterUSB
                    usb_host_pin_dp = self.settings['SYSTEM'].get('USB_HOST_PIN_DP')
                    usb_host_pin_dm = self.settings['SYSTEM'].get('USB_HOST_PIN_DM')
                    if usb_host_pin_dp is not None and usb_host_pin_dm is not None:
                        printer = PrinterUSB(printer_name, usb_host_pin_dp, usb_host_pin_dm)
                    else:
                        self.logger.error(f"        Missing USB pin definition in table/section SYSTEM (USB_HOST_PIN_DP & USB_HOST_PIN_DM), skipping printer '{printer_name}'")
                else:
                    self.logger.error(f"        DRIVER='{printer_driver}' is invalid in configuration table/section 'PRINTER:{printer_name}' (in settings.toml), skipping printer")
                if printer is not None:
                    if printer.setup(self.settings[printer_section]) is True:
                        printers[printer_name] = printer
                    else:
                        self.logger.warning(f"        Printer{printer_driver}.setup() failed for printer '{printer_name}', skipping printer")
            self.logger.info(f"    ...configuration for printer '{printer_name}' finished")
        self.runtime['printers'] = printers
        self.logger.info(f"...printers configured ({len(self.runtime['printers'])} active printers)")

        self.logger.info(f"Configuring services...")
        services = dict()
        if len(self.runtime['printers']) == 0:
            self.logger.critical(f"    No (active) printers, not activating any services")
            self.settings['ESCPOS']['SERVICES'] = []
        for service_name in self.settings['ESCPOS']['SERVICES']:
            self.logger.info(f"    Configuring service '{service_name}'...")
            service_section = f"SERVICE:{service_name}"
            if service_section not in self.settings:
                self.logger.error(f"        Configuration table/section 'SERVICE:{service_name}' (in settings.toml) not found, skipping service")
            if 'DRIVER' not in self.settings[service_section]:
                self.logger.error(f"        Missing 'DRIVER' config in table/section 'SERVICE:{service_name}' (in settings.toml), skipping service")
            if service_section in self.settings and 'DRIVER' in self.settings[service_section]:
                service = None
                service_driver = self.settings[service_section]['DRIVER'].upper()
                if service_driver == 'HTTP':
                    from .services.http import ServiceHTTP
                    service = ServiceHTTP(service_name)
                elif service_driver == 'MQTT':
                    from .services.mqtt import ServiceMQTT
                    service = ServiceMQTT(service_name)
                elif service_driver == 'TCP':
                    from .services.tcp import ServiceTCP
                    service = ServiceTCP(service_name)
                else:
                    self.logger.error(f"        DRIVER='{service_driver}' is invalid in configuration table/section 'SERVICE:{service_name}' (in settings.toml), skipping service")
                if service is not None:
                    self.settings[service_section].setdefault('PRINTERS', self.runtime['printers'].keys())
                    service2printers = {}
                    for printer_name in self.settings[service_section]['PRINTERS']:
                        if printer_name in self.runtime['printers']:
                            service2printers[printer_name] = self.runtime['printers'][printer_name]
                        if len(service2printers) == 0:
                            self.logger.warning(f"        No printers assigned to service, skipping service")
                        else:
                            if service.setup(self.settings[service_section], service2printers) is True:
                                services[service_name] = service
                                self.logger.info(f"        Assigned printers = ['{'\',\''.join(service2printers.keys())}']")
                            else:
                                self.logger.warning(f"        Service{service_driver}.setup() failed for service '{service_name}', skipping service")
            self.logger.info(f"    ...configuration for service '{service_name}' finished")
        self.runtime['services'] = services
        self.logger.info(f"...services configured ({len(self.runtime['services'])} active services)")


    def loop(self) -> bool:
        result = True
        if len(self.runtime['services']) == 0:
            result = False
        for service in self.runtime['services'].values():
            if service.loop() is False:
                result = False
        return result

