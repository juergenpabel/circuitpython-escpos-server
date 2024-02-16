# Abstract

A circuitpython application that receives ESC/POS requests via network (HTTP, MQTT &amp; RAW) and relays them to USB-connected thermal printer(s). The application waits via HTTP, MQTT and/or RAW-protocol for ESCPOS-formatted printjobs and sends them via USB to the configured thermal printer/s (without any parsing; but with additional printer reset/initialization and a paper-cut command at the end).

**Note**: The original version of this software was published in my github repo "circuitpython-picow-escpos" - but since this is not in any way confined to the Pi Pico W, I re-published this software in this repository and continue its development.

**Warning**: This software is heavily work-in-progress, thus: **before I publish release 1.0, it might not even be fully implemented or horribly broken.**

# Software

This code requires USB host-support (which for the Pi PicoW is CircuitPython 9 on master after 2024-02-15 - refer to commit [00824ad12229af15541d1431cf31f216e8e3587d](https://github.com/adafruit/circuitpython/commit/00824ad12229af15541d1431cf31f216e8e3587d)).

This circuitpython application uses [circuitpython_toml](https://github.com/elpekenin/circuitpython_toml/), [adafruit_httpserver](https://github.com/adafruit/Adafruit_CircuitPython_HTTPServer/) and [adafruit_minimqtt](https://github.com/adafruit/Adafruit_CircuitPython_MiniMQTT/) as libraries, they are provided (as copies for convenience, they might need updates at various times in the future) inside the "lib" folder and are all published under the MIT license.

Both the system-configuration (everything that circuitpython manages, including network connectivity) and application-configuration (specific to this escpos-server code) is contained in settings.toml - but the application-specific logic is inside "tables" (as the TOML spec calls them, "sections" is a more common term known from INI-files). Because CircuitPython doesn't parse (and thus not expose as environment vars) tables/sections in settings.toml, this application uses [circuitpython_toml](https://github.com/elpekenin/circuitpython_toml/) to load the application-specific configurations from settings.toml (circuitpython itself just ignores them).

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

This section describes my own hardware setup (using a PicoW), as shown in this picture:

![Picture of setup with more details](https://raw.githubusercontent.com/juergenpabel/circuitpython-escpos-server/master/resources/images/setup_detail.jpg)

The PicoW is powered using 24VDC provided by the printer (an Epson TM-T20II) via the DK-/Drawer-Kick-Connector; V+ (Pin 4) and GND (Pin 6) are sent into a step-down converter that provides 5V per USB. The PicoW plugs into the step-down converter and exposes a USB host port via GPIO (a new feature in CircuitPython 9) and connects to the USB interface on the printer (for sending ESC/POS prinbt jobs). This setup allows for a printer installation using only power (and WiFi).

# FAQ

- But why not simply use a WiFi-enabled thermal printer (Epson supports even some WiFi USB-Dongles)? That's a three-part answer:
  1. Because I don't have a WiFi-enabled model and don't want to pay for getting one
  2. I would like to have MQTT (with ESCPOS as the payload) as the interface to my printer (because MQTT is how most of my stuff at home is "linked" together)
  3. I think that the Pi PicoW (with the Infineon CYW43xxx for WiFi/BT) is probably way more securely implemented at the WiFi-layer than some add-on WiFi-board/-dongle for some thermal printer; even if that's not effectively so, there's probably a much better chance for firmware updates.

- Can't I just use a nightly build of circuitpython9 for the PicoW? Yes, as of 2024-02-15 that should work.

- Shouldn't there be an issue or even pull-request for circuitpython? Absolutely, check out [issue #8359](https://github.com/adafruit/circuitpython/issues/8359) (for context and history) and [issue #8922](https://github.com/adafruit/circuitpython/issues/8922) (for the fix).
