import os
import time
import ipaddress
import board
import wifi
import usb.core
import usb_host
import supervisor
import socketpool
from adafruit_minimqtt.adafruit_minimqtt import MQTT

g_printer = None

def on_escpos(client, topic, payload):
    print(f"Processing MQTT message on topic '{topic}' with a payload of {len(payload)} bytes")
    g_printer.write(1, b'\x1b\x40')
    g_printer.write(1, b'\x1b\x64\x04')
    for offset in range(0, len(payload), 64):
        g_printer.write(1, payload[offset:offset+64])
    g_printer.write(1, b'\x1b\x64\x08')
    g_printer.write(1, b'\x1b\x6d')

    
if os.getenv('DEBUG') is not None and bool(os.getenv('DEBUG')) is True:
    while supervisor.runtime.serial_connected is False:
        time.sleep(1)
print(f"Connecting to SSID '{os.getenv('WIFI_SSID')}'...")
wifi.radio.connect(os.getenv('WIFI_SSID'), os.getenv('WIFI_PSK'))
print(f"IPv4: {wifi.radio.ipv4_address}")
time.sleep(1)
print("\nPicoW USB/ESCPOS driver")

print(f"Connecting to USB printer '{os.getenv('PRINTER_USB_VID', '04b8')}:{os.getenv('PRINTER_USB_PID', '0e15')}'...")
usb_host.Port(board.GP26, board.GP27)
while g_printer is None:
    g_printer = usb.core.find(idVendor=os.getenv('PRINTER_USB_VID', '04b8'), idProduct=os.getenv('PRINTER_USB_PID', '0e15'))
    time.sleep(1)
print(f"{g_printer.idVendor:04x}:{g_printer.idProduct:04x} {g_printer.manufacturer} / {g_printer.product} (#{g_printer.serial_number})")
g_printer.set_configuration()

print(f"Connecting to MQTT broker '{os.getenv('MQTT_BROKER_IPV4', '192.168.1.1')}'...")
mqtt_client = MQTT(broker=os.getenv('MQTT_BROKER_IPV4', '192.168.1.1'),
                   username=os.getenv('MQTT_BROKER_USER', None),
                   password=os.getenv('MQTT_BROKER_PASS', None),
                   socket_pool=socketpool.SocketPool(wifi.radio),
                   use_binary_mode=True)
while mqtt_client.is_connected() is False:
    mqtt_client.connect()
    time.sleep(1)

mqtt_client.on_message = on_escpos
mqtt_client.subscribe(os.getenv('MQTT_BROKER_TOPIC', 'printer/+/escpos'))
print(f"Connected to MQTT broker, running loop() now")
while mqtt_client.is_connected() is True:
    mqtt_client.loop()
print(f"Disconnected from MQTT broker '{os.getenv('MQTT_BROKER_IPV4', '192.168.1.1')}' - restarting...")
supervisor.reload()

