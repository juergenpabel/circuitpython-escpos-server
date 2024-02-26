# Abstract

A circuitpython application that receives ESC/POS requests via network (HTTP, MQTT &amp; RAW) and relays them to USB-connected thermal printer(s). The application waits via HTTP, MQTT and/or RAW-protocol for ESCPOS-formatted printjobs and sends them via USB to the configured thermal printer/s (without any parsing; but -optionally- with additional printer reset/initialization commands before the printjob and a paper-cut command after the printjob).

**Note**: The original version of this software was published in my github repo "circuitpython-picow-escpos" - but since this is not in any way confined to the Pi Pico W, I re-published this software in this repository and continue its development here.

# Software

This circuitpython application uses [circuitpython_toml](https://github.com/elpekenin/circuitpython_toml/), [adafruit_httpserver](https://github.com/adafruit/Adafruit_CircuitPython_HTTPServer/), [adafruit_logging](https://github.com/adafruit/Adafruit_CircuitPython_Logging), [adafruit_minimqtt](https://github.com/adafruit/Adafruit_CircuitPython_MiniMQTT/) and [circuitpython_usyslog](https://github.com/ageagainstthemachine/circuitpython-usyslog) as libraries, they are provided (as copies for convenience, they might need updates at various times in the future) inside the "lib" folder and are all published under the MIT license.

Documentation for configuring the application is [in the Wiki](https://github.com/juergenpabel/circuitpython-escpos-server/wiki/Configuration).

**For USB-connected printers USB host-support in CircuitPython is required** (which for the Pi PicoW is CircuitPython 9 on master after 2024-02-15 - refer to commit [00824ad12229af15541d1431cf31f216e8e3587d](https://github.com/adafruit/circuitpython/commit/00824ad12229af15541d1431cf31f216e8e3587d)), which for the PicoW is NOT in CircuitPython 9.0.0-beta.0 but should be in 9.0.0-beta.1 (or whatever the next beta release will be called).

# Hardware

This section describes my own hardware setup (using a PicoW), as shown in this picture:

![Picture of setup with more details](https://raw.githubusercontent.com/juergenpabel/circuitpython-escpos-server/master/resources/images/setup_detail.jpg)

The PicoW is powered using 24VDC provided by the printer (an Epson TM-T20II) via the DK-/Drawer-Kick-Connector; V+ (Pin 4) and GND (Pin 6) are sent into a step-down converter that provides 5V per USB. The PicoW plugs into the step-down converter and exposes a USB host port via GPIO (a new feature for the PicoW in CircuitPython 9) and connects to the USB interface on the printer (for sending ESC/POS prinbt jobs). This setup allows for a printer installation using only one power cord (and WiFi).

# FAQ

- But why not simply use a WiFi-enabled thermal printer (Epson supports even some WiFi USB-Dongles)? That's a three-part answer:
  1. Because I don't have a WiFi-enabled model and don't want to pay for getting one
  2. I would like to have MQTT (with ESCPOS as the payload) as the interface to my printer (because MQTT is how most of my stuff at home is "linked" together)
  3. I think that the Pi PicoW (with the Infineon CYW43xxx for WiFi/BT) is probably way more securely implemented at the WiFi-layer than some add-on WiFi-board/-dongle for some thermal printer; even if that's not effectively so, there's probably a much better chance for firmware updates.

- Which circuit python version for my &lt;board-name&gt;? Probably Circuitpython 8, it just needs [usb_host](https://docs.circuitpython.org/en/8.2.x/shared-bindings/usb_host/index.html) support (see the "Available on these boards" list) - the list is rather short, though.

- Which circuit python version for PicoW? As of 2024-02-15: use a development build, take a look at their [S3 bucket for the PicoW](https://adafruit-circuit-python.s3.amazonaws.com/index.html?prefix=bin/raspberry_pi_pico_w/).
  
- Why not provide the libs as MPYs for better performance and reduced memory consumption? Because CircuitPython 9 is still in beta and for the PicoW (my personal setup) it still needs the development builds, which are incompatible with the released MPYs of the other projects.

