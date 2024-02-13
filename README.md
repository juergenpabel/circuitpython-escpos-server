# Abstract

A circuitpython application that receives ESC/POS requests via network (HTTP, MQTT &amp; RAW) and relays them to USB-connected thermal printer(s). The application waits via HTTP, MQTT and/or RAW-protocol for ESCPOS-formatted printjobs and sends them via USB to the configured thermal printer/s (without any parsing; but with an additional paper-cut command at the end).

**Note**: The original version of this software was published in my github repo "circuitpython-picow-escpos" - but since this is not in any way confined to the Pi Pico W, I re-published this software in this repository and continue its development.

**Warning 0**: This software is heavily work-in-progress, thus: **before I publish release 1.0, it might not even be fully implemented or horribly broken.**

# Software

**Warning 1**: This code requires USB host-support (which for the Pi Pico W is CircuitPython 9).

**Warning 2 (for Pi Pico W)**: The current CircuitPython implementation status (as of 2024-02-13 on master) has a non-working USB-Host support for the Pi PicoW due to insufficient PIO space. The following diff adapts the PIO configuration into a working state (by simply swapping assignments for PIO #0 and #1):
```
diff --git a/ports/raspberrypi/common-hal/usb_host/Port.c b/ports/raspberrypi/common-hal/usb_host/Port.c
index 93d19acd6..6b9aeae55 100644
--- a/ports/raspberrypi/common-hal/usb_host/Port.c
+++ b/ports/raspberrypi/common-hal/usb_host/Port.c
@@ -122,8 +122,8 @@ usb_host_port_obj_t *common_hal_usb_host_port_construct(const mcu_pin_obj_t *dp,
     pio_usb_configuration_t pio_cfg = PIO_USB_DEFAULT_CONFIG;
     pio_cfg.skip_alarm_pool = true;
     pio_cfg.pin_dp = dp->number;
-    pio_cfg.pio_tx_num = 0;
-    pio_cfg.pio_rx_num = 1;
+    pio_cfg.pio_rx_num = 0;
+    pio_cfg.pio_tx_num = 1;
     // PIO with room for 22 instructions
     // PIO with room for 31 instructions and two free SM.
     if (!_has_program_room(pio_cfg.pio_tx_num, 22) || _sm_free_count(pio_cfg.pio_tx_num) < 1 ||
```
This circuitpython application uses on [adafruit_minimqtt](https://github.com/adafruit/Adafruit_CircuitPython_MiniMQTT/) and [circuitpython_toml](https://github.com/elpekenin/circuitpython_toml/) as libraries, they are provided (as copies, might need updates at various times in the future) inside the "lib" folder and are both published under the MIT license.

Both the system-configuration (everything that circuitpython manages, including network connectivity) and application-configuration (specific to this escpos-server code) is contained in settings.toml - but the application-specific logic is inside "tables" (as the TOML spec calls them, "sections" is a more common term known from INI-files). Because CircuitPython doesn't parse (and thus not expose as environment vars) tables/sections in settings.toml, this application uses circuitpython_toml to load the application-specific configurations from settings.toml (circuitpython itself just ignores them).

**TODO - update this config section**
- WIFI_SSID: The SSID of the AP to connect to (I didn't want to use CIRCUITPY_WIFI_SSID due to the included web interface; not needed/wanted)
- WIFI_PSK: The password for the network
- PRINTER_USB_VID: The USB vendor ID of the attached thermal printer (in hex notation, like "04b8" for Epson)
- PRINTER_USB_PID: The USB product ID of the attached thermal printer (in hex notation, like "0e15" for TM-T20II)
- MQTT_BROKER_IPV4: MQTT server address (DNS or IPv4)
- MQTT_BROKER_USER: MQTT username (or unset for anonymous)
- MQTT_BROKER_PASS: MQTT password (or unset for anonymous)
- MQTT_BROKER_TOPIC: MQTT topic to listen on for ESCPOS-formatted print data
- DEBUG: If set (to any value that yields *True* when passed to *bool()*) the application will wait on startup for a serial connection to the board (this is for debugging purposes so that nothing interesting happens before the serial connection has been established)

# Hardware

This section describes my own hardware setup (using a Pico W), as shown in this picture:

![Picture of setup with more details](https://raw.githubusercontent.com/juergenpabel/circuitpython-escpos-server/master/resources/images/setup_detail.jpg)

The PicoW is powered using 24VDC provided by the printer (an Epson TM-T20II) via the DK-/Drawer-Kick-Connector; V+ (Pin 4) and GND (Pin 6) are sent into a step-down converter that provides 5V per USB. The PicoW plugs into the step-down converter and exposes a USB host port via GPIO (a new feature in CircuitPython 9) and connects to the USB interface on the printer (for sending ESC/POS prinbt jobs). This setup allows for printer installations using only power (and WiFi).

# FAQ

- But why not simply use a WiFi-enabled thermal printer (Epson supports even some WiFi USB-Dongles)? That's a three-part answer:
  1. Because I don't have a WiFi-enabled model and don't want to pay for getting one
  2. I would like to have MQTT (with ESCPOS as the payload) as the interface to my printer (because MQTT is how most of my stuff at home is "linked" together)
  3. I think that the Pi PicoW (with the Infineon CYW43xxx for WiFi/BT) is probably way more securely implemented at the WiFi-layer than some add-on WiFi-board/-dongle for some thermal printer; even if that's not effectively so, there's probably a much better chance for firmware updates.

- Can't I just use a nightly build of circuitpython? Once the PIO issue (see diff from above) has been resolved: Probably (that diff is the only diff I applied for my builds).

- Shouldn't there be an issue or even pull-request for circuitpython? Check out [issue #8359](https://github.com/adafruit/circuitpython/issues/8359)

