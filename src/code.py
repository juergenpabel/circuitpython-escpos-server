import time
import board
import wifi
import usb.core
import usb_host
import supervisor
import toml

g_runtime = {}
g_runtime['printers'] = dict()
g_runtime['services'] = list()

g_config = toml.load('settings.toml')
g_config.setdefault('SYSTEM', {'DEBUG': False})
g_config['SYSTEM.DEBUG'] = bool(g_config['SYSTEM.DEBUG'])
g_config.setdefault('ESCPOS', {})
g_config.setdefault('PRINTER:DEBUG', {'DRIVER': 'DEBUG'})

if g_config['SYSTEM.DEBUG'] is True:
    while supervisor.runtime.serial_connected is False:
        time.sleep(1)

if 'WIFI_SSID' in g_config:
    mac = ':'.join(['{:02X}'.format(i) for i in wifi.radio.mac_address])
    print(f"Connecting to SSID '{g_config['WIFI_SSID']}' with MAC='{mac}'...")
    wifi.radio.connect(g_config['WIFI_SSID'], g_config['WIFI_PSK'])
    print(f"...connected with IPv4={wifi.radio.ipv4_address}")
    time.sleep(1)

print(f"Configuring printers...")
for printer_name in g_config['ESCPOS']['PRINTERS']:
    printer_section = f"PRINTER:{printer_name}"
    if printer_section in g_config and 'DRIVER' in g_config[printer_section]:
        printer = None
        printer_driver = g_config[printer_section]['DRIVER'].upper()
        if printer_driver == 'DEBUG':
            from printers.debug import PrinterDebug
            printer = PrinterDebug()
        elif printer_driver == 'USB':
            from printers.usb import PrinterUSB
            printer = PrinterUSB(g_config['SYSTEM.DEBUG'])
        else:
            print(f"    ERROR in configuration for printer '{printer_name}': unknown driver type '{printer_driver}', skipping printer")
        if printer is not None:
            if printer.setup(g_config[printer_section]) is True:
                print(f"    adding printer '{printer_name}'")
                g_runtime['printers'][printer_name] = printer
            else:
                print(f"    printer '{printer_name}' returned error during setup(), skipping printer")                
print(f"...printers configured ({len(g_runtime['printers'])} active printers)")

print(f"Configuring services...")
if 'HTTP' in g_config['ESCPOS.SERVICES'] and 'SERVICE:HTTP' in g_config:
    from services.http import ServiceHTTP
    g_config['SERVICE:HTTP'].setdefault('SERVER_IPV4', str(wifi.radio.ipv4_address))
    g_config['SERVICE:HTTP'].setdefault('SERVER_PATH', '/')
    service = ServiceHTTP(g_config['SYSTEM.DEBUG'])
    if service.setup(g_config['SERVICE:HTTP'], g_runtime['printers']) is True:
        g_runtime['services'].append(service)
if 'MQTT' in g_config['ESCPOS.SERVICES'] and 'SERVICE:MQTT' in g_config:
    from services.mqtt import ServiceMQTT
    g_config['SERVICE:MQTT'].setdefault('BROKER_USER', None)
    g_config['SERVICE:MQTT'].setdefault('BROKER_PASS', None)
    service = ServiceMQTT(g_config['SYSTEM.DEBUG'])
    if service.setup(g_config['SERVICE:MQTT'], g_runtime['printers']) is True:
        g_runtime['services'].append(service)
if 'TCP' in g_config['ESCPOS.SERVICES'] and 'SERVICE:TCP' in g_config:
    from services.tcp  import ServiceTCP
    g_config['SERVICE:TCP'].setdefault('SERVER_IPV4', str(wifi.radio.ipv4_address))
    g_config['SERVICE:TCP'].setdefault('SERVER_PORT', 9100)
    g_config['SERVICE:TCP'].setdefault('CLIENT_TIMEOUT', 1)
    service = ServiceTCP(g_config['SYSTEM.DEBUG'])
    if service.setup(g_config['SERVICE:TCP'], g_runtime['printers']) is True:
        g_runtime['services'].append(service)
print(f"...services configured ({len(g_runtime['services'])} active services)")

print("Running server loop...")
if g_runtime['printers'] is not None:
    service_loop = True
    while bool(service_loop) is True:
        for service in g_runtime['services']:
            service_loop &= service.loop()
print(f"...server loop exited - reloading application in 5 seconds")
time.sleep(5)
supervisor.reload()

