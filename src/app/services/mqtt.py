import time
import wifi
import socketpool
from adafruit_minimqtt.adafruit_minimqtt import MQTT as MQTTClient

from . import Service


class ServiceMQTT(Service):
    mqtt_client: MQTTClient = None


    def __init__(self, debug: bool):
        Service.__init__(self, debug)


    def setup(self, config: toml.Dotty, printers: dict) -> bool:
        Service.setup(self, config, printers)
        if 'BROKER_IPV4' not in config:
            print("ERROR: Missing 'BROKER_IPV4' config in table/secion 'SERVICE:MQTT' in settings.toml, disabling service MQTT")
            return False
        if 'BROKER_TOPIC' not in config:
            print("ERROR: Missing 'BROKER_TOPIC' config in table/secion 'SERVICE:MQTT' in settings.toml, disabling service MQTT")
            return False
        print(f"    Connecting to MQTT broker '{config.get('BROKER_IPV4')}'...")
        self.mqtt_client = MQTTClient(broker=config.get('BROKER_IPV4'),
                                      username=config.get('BROKER_USER'),
                                      password=config.get('BROKER_PASS'),
                                      socket_pool=socketpool.SocketPool(wifi.radio),
                                      use_binary_mode=True)
        while self.mqtt_client.is_connected() is False:
            self.mqtt_client.connect()
            time.sleep(1)
        print(f"    ...now connected to MQTT broker '{config.get('BROKER_IPV4')}'")
        self.mqtt_client.on_message = self._on_mqtt_message
        self.mqtt_client.subscribe(config.get('BROKER_TOPIC'))
        self.mqtt_client.loop(1)
        return True


    def loop(self) -> bool:
        if self.mqtt_client is not None:
            self.mqtt_client.loop(1)
            if self.mqtt_client.is_connected() is True:
                return True
        return False

 
    def _on_mqtt_message(self, client, topic, payload):
        if self.debug is True:
            print(f"Processing MQTT message on topic '{topic}' with a payload of {len(payload)} bytes")
        for printer in self.printers.values():
            printer.write_init()
            for offset in range(0, len(payload), 64):
                printer.write(bytes(payload[offset:offset+64]))
            printer.write_fini()

