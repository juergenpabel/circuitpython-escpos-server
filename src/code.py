import os
import time
import wifi
import supervisor
import socketpool

from app import Server
from app.util.log import Log


print("\n\ncode.py")
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
                print(f"...connected with IPv4='{wifi.radio.ipv4_address}'")
                time.sleep(1)
            except ConnectionError:
                wifi_offline_grace_secs = int(os.getenv('WIFI_OFFLINE_GRACE_PERIOD', '300'))
                print(f"...could not connected to SSID '{wifi_ssid}' (WIFI_SSID); waiting for {wifi_offline_grace_secs} seconds (WIFI_OFFLINE_GRACE_PERIOD), than reloading circuitpython app")
                time.sleep(wifi_offline_grace_secs)
                supervisor.reload()

server = Server()
server.setup()
server.getLogger().info(f"Running server loop (IPv4='{wifi.radio.ipv4_address}')...")
try:
    wifi_healthy_check_secs = float(os.getenv('WIFI_HEALTH_CHECK_PERIOD', '60'))
    wifi_healthy_timestamp = time.monotonic()
    wifi_offline_grace_secs = float(os.getenv('WIFI_OFFLINE_GRACE_PERIOD', '300'))
    wifi_offline_timestamp = None
    loop_result = True
    while loop_result is True:
        if wifi_offline_timestamp is None:
            if wifi.radio.connected is False:
                server.getLogger().info(f"    WIFI disconnected, waiting for {int(wifi_offline_grace_secs)} seconds (WIFI_OFFLINE_GRACE_PERIOD) to come back online")
                wifi_offline_timestamp = time.monotonic()
            else:
                if time.monotonic() > wifi_healthy_timestamp + wifi_healthy_check_secs:
                    wifi_healthy_timestamp = time.monotonic()
                    if wifi.radio.ping(wifi.radio.ipv4_gateway) is None:
                        server.getLogger().info(f"    WIFI connected but IPv4 gateway ({wifi.radio.ipv4_gateway}) not reachable")
                        wifi_offline_timestamp = time.monotonic()
        else:
            if wifi.radio.connected is True:
                server.getLogger().info(f"    WIFI reconnected (IPv4={wifi.radio.ipv4_address})")
                wifi_offline_timestamp = None
            else:
                if time.monotonic() > wifi_offline_timestamp + wifi_offline_grace_secs:
                    server.getLogger().critical(f"    WIFI offline for more than {int(wifi_offline_grace_secs)} seconds (WIFI_OFFLINE_GRACE_PERIOD), resetting NOW")
                    import microcontroller
                    microcontroller.reset()
        loop_result = server.loop()
except BaseException as e:
    server.getLogger().critical(f"    FATAL: <{type(e).__name__}> {str(e)}")
server.getLogger().info(f"...server loop exited - restarting in 5 seconds")
time.sleep(5)
supervisor.reload()

