import time
import wifi
import socketpool
from adafruit_minimqtt.adafruit_minimqtt import MQTT as MQTTClient

from . import Service
from app.util.log import Log

class ServiceMQTT(Service):
    mqtt_client: MQTTClient = None

    def __init__(self, name:str ):
        Service.__init__(self, name)

    def setup(self, config: dict, printers: dict) -> bool:
        Service.setup(self, config, printers)
        if 'BROKER_IPV4' not in config:
            Log().getLogger(f"SERVICE:{self.name}").error("missing 'BROKER_IPV4' setting in table/secion 'SERVICE:{self.name}' in settings.toml, disabling service")
            return False
        if 'BROKER_USER' not in config:
            config['BROKER_USER'] = None
        if 'BROKER_PASS' not in config:
            config['BROKER_PASS'] = None
        if 'BROKER_TOPIC' not in config:
            Log().getLogger(f"SERVICE:{self.name}").error("missing 'BROKER_TOPIC' setting in table/secion 'SERVICE:{self.name}' in settings.toml, disabling service")
            return False
        Log().getLogger(f"SERVICE:{self.name}").info(f"    Connecting to MQTT broker '{config['BROKER_IPV4']}'...")
        self.mqtt_client = MQTTClient(broker=config['BROKER_IPV4'],
                                      username=config['BROKER_USER'],
                                      password=config['BROKER_PASS'],
                                      socket_pool=socketpool.SocketPool(wifi.radio),
                                      use_binary_mode=True)
        while self.mqtt_client.is_connected() is False:
            self.mqtt_client.connect()
            time.sleep(1)
        Log().getLogger(f"SERVICE:{self.name}").info(f"    ...now connected to MQTT broker '{config['BROKER_IPV4']}'")
        self.mqtt_client.on_message = self._on_mqtt_message
        self.mqtt_client.subscribe(config['BROKER_TOPIC'])
        self.mqtt_client.loop(1)
        return True

    def loop(self) -> bool:
        if self.mqtt_client is not None:
            self.mqtt_client.loop(1)
            if self.mqtt_client.is_connected() is True:
                return True
        return False
 
    def _on_mqtt_message(self, client, topic, payload):
        Log().getLogger(f"SERVICE:{self.name}").debug(f"processing MQTT message on topic '{topic}' with a payload of {len(payload)} bytes")
        for printer in self.printers.values():
            printer.write_init()
            for offset in range(0, len(payload), 64):
                printer.write(bytes(payload[offset:offset+64]))
            printer.write_fini()

