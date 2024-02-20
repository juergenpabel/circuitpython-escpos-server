import os
import wifi
import toml


class Server:
    debug:   bool = False
    runtime: dict
    config:  toml.Dotty

    def __init__(self, debug):
        self.debug = debug
        self.runtime = { 'printers': {}, 'services': {} }
        self.config = toml.load('settings.toml')
        self.config.setdefault('SYSTEM', {})
        self.config.setdefault('ESCPOS', {'PRINTERS': {}, 'SERVICES': {}})
        self.config.setdefault('PRINTER:DEBUG', {'DRIVER': 'DEBUG'})


    def setup(self):
        print(f"Configuring printers...")
        for printer_name in self.config['ESCPOS']['PRINTERS']:
            print(f"    Configuring printer '{printer_name}'...")
            printer_section = f"PRINTER:{printer_name}"
            if printer_section in self.config and 'DRIVER' in self.config[printer_section]:
                printer = None
                printer_driver = self.config[printer_section]['DRIVER'].upper()
                if printer_driver == 'DEBUG':
                    from .printers.debug import PrinterDEBUG
                    printer = PrinterDEBUG()
                elif printer_driver == 'USB':
                    from .printers.usb import PrinterUSB
                    usb_host_pin_dp = self.config['SYSTEM'].get('USB_HOST_PIN_DP')
                    usb_host_pin_dm = self.config['SYSTEM'].get('USB_HOST_PIN_DM')
                    if usb_host_pin_dp is not None and usb_host_pin_dm is not None:
                        printer = PrinterUSB(usb_host_pin_dp, usb_host_pin_dm, self.debug)
                    else:
                        print(f"        ERROR: in configuration for printer '{printer_name}': missing pin definition in table/section SYSTEM (USB_HOST_PIN_DP & USB_HOST_PIN_DM), skipping printer")
                else:
                    print(f"        ERROR: in configuration for printer '{printer_name}': unknown driver type '{printer_driver}', skipping printer")
                if printer is not None:
                    if printer.setup(self.config[printer_section]) is True:
                        self.runtime['printers'][printer_name] = printer
                    else:
                        print(f"        WARNING: Printer{printer_driver}.setup() failed for printer '{printer_name}', skipping printer")
            print(f"    ...configuration for printer '{printer_name}' finished")
        print(f"...printers configured ({len(self.runtime['printers'])} active printers)")

        print(f"Configuring services...")
        for service_name in self.config['ESCPOS']['SERVICES']:
            print(f"    Configuring service '{service_name}'...")
            service_section = f"SERVICE:{service_name}"
            if service_section not in self.config:
                print(f"        ERROR: configuration table/section 'SERVICE:{service_name}' not found, skipping service")
            if 'DRIVER' not in self.config[service_section]:
                print(f"        ERROR: missing 'DRIVER' config in table/section 'SERVICE:{service_name}', skipping service")
            if service_section in self.config and 'DRIVER' in self.config[service_section]:
                service = None
                service_driver = self.config[service_section]['DRIVER'].upper()
                if service_driver == 'HTTP':
                    self.config[service_section].setdefault('SERVER_IPV4', str(wifi.radio.ipv4_address))
                    self.config[service_section].setdefault('SERVER_PORT', 8080)
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
                    print(f"        ERROR: unknown driver type '{service_driver}' in configuration table/section 'SERVICE:{service_name}', skipping service")
                if service is not None:
                    self.config[service_section].setdefault('PRINTERS', self.runtime['printers'].keys())
                    service2printers = {}
                    for printer_name in self.config[service_section]['PRINTERS']:
                        if printer_name in self.runtime['printers']:
                            service2printers[printer_name] = self.runtime['printers'][printer_name]
                        if len(service2printers) == 0:
                            print(f"        WARNING: No printers assigned to service, skipping service")
                        else:
                            if service.setup(self.config[service_section], service2printers) is True:
                                self.runtime['services'][service_name] = service
                                print(f"        INFO: Assigned printers = [{','.join(service2printers.keys())}]")
                            else:
                                print(f"        WARNING: Service{service_driver}.setup() failed for service '{service_name}', skipping service")
            print(f"    ...configuration for service '{service_name}' finished")
        print(f"...services configured ({len(self.runtime['services'])} active services)")


    def loop(self) -> bool:
        result = True
        for service in self.runtime['services'].values():
            if service.loop() is False:
                result = False
        return result

