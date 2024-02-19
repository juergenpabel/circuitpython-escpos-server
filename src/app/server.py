import os
import wifi
import toml


class Server:
    debug:   bool = False
    runtime: dict
    config:  toml.Dotty

    def __init__(self):
        if 'DEBUG' in os.environ and bool(os.environ['DEBUG']) is True:
            self.debug = True
        self.runtime = { 'printers': {}, 'services': {} }
        self.config = toml.load('settings.toml')
        self.config.setdefault('SYSTEM', {})
        self.config.setdefault('ESCPOS', {'PRINTERS': {}, 'SERVICES': {}})
        self.config.setdefault('PRINTER:DEBUG', {'DRIVER': 'DEBUG'})


    def setup(self):
        print(f"Configuring printers...")
        for printer_name in self.config['ESCPOS']['PRINTERS']:
            printer_section = f"PRINTER:{printer_name}"
            if printer_section in self.config and 'DRIVER' in self.config[printer_section]:
                printer = None
                printer_driver = self.config[printer_section]['DRIVER'].upper()
                if printer_driver == 'DEBUG':
                    from .printers.debug import PrinterDEBUG
                    printer = PrinterDEBUG()
                elif printer_driver == 'USB':
                    from .printers.usb import PrinterUSB
                    printer = PrinterUSB(self.debug)
                else:
                    print(f"    ERROR in configuration for printer '{printer_name}': unknown driver type '{printer_driver}', skipping printer")
                if printer is not None:
                    if printer.setup(self.config[printer_section]) is True:
                        self.runtime['printers'][printer_name] = printer
                        print(f"    Added printer '{printer_name}'")
                    else:
                        print(f"    WARNING Printer{printer_driver}.setup() failed for printer '{printer_name}', skipping printer")
        print(f"...printers configured ({len(self.runtime['printers'])} active printers)\n")

        print(f"Configuring services...")
        for service_name in self.config['ESCPOS']['SERVICES']:
            service_section = f"SERVICE:{service_name}"
            if service_section in self.config and 'DRIVER' in self.config[service_section]:
                service = None
                service_driver = self.config[service_section]['DRIVER'].upper()
                if service_driver == 'HTTP':
                    self.config[service_section].setdefault('SERVER_IPV4', str(wifi.radio.ipv4_address))
                    self.config[service_section].setdefault('SERVER_PATH', '/')
                    from .services.http import ServiceHTTP
                    service = ServiceHTTP(self.debug)
                elif service_driver == 'MQTT':
                    self.config[service_section].setdefault('BROKER_USER', None)
                    self.config[service_section].setdefault('BROKER_PASS', None)
                    from .services.mqtt import ServiceMQTT
                    service = ServiceMQTT(self.debug)
                elif service_driver == 'TCP':
                    self.config[service_section].setdefault('SERVER_IPV4', str(wifi.radio.ipv4_address))
                    self.config[service_section].setdefault('SERVER_PORT', 9100)
                    self.config[service_section].setdefault('CLIENT_TIMEOUT', 1)
                    from .services.tcp import ServiceTCP
                    service = ServiceTCP(self.debug)
                else:
                    print(f"    ERROR in configuration for service '{service_name}': unknown driver type '{service_driver}', skipping service")
                if service is not None:
                    if service.setup(self.config[service_section], self.runtime['printers']) is True:
                        self.runtime['services'][service_name] = service
                        print(f"    Added service '{service_name}'")
                    else:
                        print(f"    WARNING Service{service_driver}.setup() failed for service '{service_name}', skipping service")
        print(f"...services configured ({len(self.runtime['services'])} active services)\n")


    def loop(self) -> bool:
        result = True
        for service in self.runtime['services'].values():
            if service.loop() is False:
                result = False
        return result

