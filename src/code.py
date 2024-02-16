import time
import board
import wifi
import usb.core
import usb_host
import supervisor
import toml
from printers.debug import PrinterDebug

g_runtime = {}
g_runtime['printer'] = None
g_runtime['services'] = list()

g_config = toml.load('settings.toml')
g_config.setdefault('SYSTEM', {'DEBUG': False})
g_config['SYSTEM.DEBUG'] = bool(g_config['SYSTEM.DEBUG'])
g_config.setdefault('ESCPOS', {})

if g_config['SYSTEM.DEBUG'] is True:
    g_runtime['printer'] = PrinterDebug(g_config['SYSTEM.DEBUG'])
    while supervisor.runtime.serial_connected is False:
        time.sleep(1)

if 'WIFI_SSID' in g_config:
    mac = ':'.join(['{:02X}'.format(i) for i in wifi.radio.mac_address])
    print(f"Connecting to SSID '{g_config['WIFI_SSID']}' with MAC='{mac}'...")
    wifi.radio.connect(g_config['WIFI_SSID'], g_config['WIFI_PSK'])
    print(f"...connected with IPv4={wifi.radio.ipv4_address}")
    time.sleep(1)

print("Configuring ESCPOS server...")
printer_usb_vid = g_config['SYSTEM'].get('PRINTER_USB_VID')
printer_usb_pid = g_config['SYSTEM'].get('PRINTER_USB_PID')
if printer_usb_vid is not None and printer_usb_pid is not None:
    print(f"Connecting to USB printer '{printer_usb_vid}:{printer_usb_pid}'...")
    usb_host.Port(board.GP26, board.GP27)
    printer = None
    while printer is None:
        printer = usb.core.find(idVendor=printer_usb_vid, idProduct=printer_usb_pid)
        time.sleep(1)
    print(f"...connected to {printer.idVendor:04x}:{printer.idProduct:04x} {printer.manufacturer} / {printer.product} (#{printer.serial_number})")
    printer.set_configuration()
    g_runtime['printer'] = printer
if 'HTTP' in g_config['ESCPOS.SERVICES'] and 'SERVICE:HTTP' in g_config:
    from services.http import ServiceHTTP
    g_config['SERVICE:HTTP'].setdefault('SERVER_IPV4', str(wifi.radio.ipv4_address))
    g_config['SERVICE:HTTP'].setdefault('SERVER_PATH', '/')
    service = ServiceHTTP(g_config['SYSTEM.DEBUG'])
    if service.setup(g_config['SERVICE:HTTP'], g_runtime['printer']) is True:
        g_runtime['services'].append(service)
if 'MQTT' in g_config['ESCPOS.SERVICES'] and 'SERVICE:MQTT' in g_config:
    from services.mqtt import ServiceMQTT
    g_config['SERVICE:MQTT'].setdefault('BROKER_USER', None)
    g_config['SERVICE:MQTT'].setdefault('BROKER_PASS', None)
    service = ServiceMQTT(g_config['SYSTEM.DEBUG'])
    if service.setup(g_config['SERVICE:MQTT'], g_runtime['printer']) is True:
        g_runtime['services'].append(service)
if 'TCP' in g_config['ESCPOS.SERVICES'] and 'SERVICE:TCP' in g_config:
    from services.tcp  import ServiceTCP
    g_config['SERVICE:TCP'].setdefault('SERVER_IPV4', str(wifi.radio.ipv4_address))
    g_config['SERVICE:TCP'].setdefault('SERVER_PORT', 9100)
    g_config['SERVICE:TCP'].setdefault('CLIENT_TIMEOUT', 1)
    service = ServiceTCP(g_config['SYSTEM.DEBUG'])
    if service.setup(g_config['SERVICE:TCP'], g_runtime['printer']) is True:
        g_runtime['services'].append(service)
print(f"...ESCPOS server configured ({len(g_runtime['services'])} active services)")

print("Running ESCPOS service loop...")
if g_runtime['printer'] is not None:
    service_loop = True
    while bool(service_loop) is True:
        for service in g_runtime['services']:
            service_loop = service_loop and service.loop()
print(f"...ESCPOS service loop exited - reloading application in 5 seconds")
time.sleep(5)
supervisor.reload()

