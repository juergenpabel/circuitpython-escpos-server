import os
import time
import wifi
import supervisor
from app import Server

g_debug: bool = False

print("\n\ncircuitpython-escpos-server")
if g_debug is False:
    if bool(os.getenv('DEBUG', False)) is True:
        g_debug = True

if wifi.radio.connected is False:
    circuitpython_wifi_ssid = os.getenv('CIRCUITPY_WIFI_SSID')
    if circuitpython_wifi_ssid is None:
        wifi_ssid = os.getenv('WIFI_SSID', None)
        wifi_psk  = os.getenv('WIFI_PSK',  None)
        if wifi_ssid is not None:
            mac = ':'.join(['{:02X}'.format(i) for i in wifi.radio.mac_address])
            print(f"Connecting to SSID '{wifi_ssid}' (wifi.Radio.mac_address='{mac}')...")
            try:
                wifi.radio.connect(wifi_ssid, wifi_psk)
                print(f"...connected with IPv4={wifi.radio.ipv4_address}")
            except ConnectionError:
                wifi_offline_grace_secs = int(os.getenv('WIFI_OFFLINE_GRACE_PERIOD', '300'))
                print(f"...could not connected to SSID '{wifi_ssid}' (WIFI_SSID); waiting for {wifi_offline_grace_secs} seconds (WIFI_OFFLINE_GRACE_PERIOD), than reloading circuitpython app")
                time.sleep(wifi_offline_grace_secs)
                supervisor.reload()

server = Server(g_debug)
server.setup()
print(f"Running server loop (IPv4={wifi.radio.ipv4_address})...")
try:
    wifi_offline_timestamp_secs = None
    wifi_offline_grace_secs = float(os.getenv('WIFI_OFFLINE_GRACE_PERIOD', '300'))
    loop_result = True
    while loop_result is True:
        if wifi_offline_timestamp_secs is None:
            if wifi.radio.connected is False and wifi.radio.ap_active is False:
                print(f"    INFO: WIFI disconnected, waiting for {int(wifi_offline_grace_secs)} seconds (WIFI_OFFLINE_GRACE_PERIOD) to come back online")
                wifi_offline_timestamp_secs = time.monotonic()
        else:
            if wifi.radio.connected is True:
                print(f"    INFO: WIFI reconnected (IPv4={wifi.radio.ipv4_address})")
                wifi_offline_timestamp_secs = None
            else:
                if time.monotonic() > wifi_offline_timestamp_secs + wifi_offline_grace_secs:
                    print(f"    FATAL: WIFI offline for more than {int(wifi_offline_grace_secs)} seconds (WIFI_OFFLINE_GRACE_PERIOD), resetting NOW")
                    import microcontroller
                    microcontroller.reset()
        loop_result = server.loop()
except BaseException as e:
    print(f"    FATAL: <{type(e).__name__}> {str(e)}")
print(f"...server loop exited - restarting in 5 seconds")
time.sleep(5)
supervisor.reload()

