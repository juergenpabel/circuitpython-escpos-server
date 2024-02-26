# Abstract

A circuitpython application that receives ESC/POS requests via network (HTTP, MQTT &amp; TCP) and relays them to connected thermal printer(s). The application waits via HTTP, MQTT and/or TCP for ESCPOS-formatted printjobs and sends them to the configured thermal printer/s (without any parsing; but -optionally- with additional printer reset/initialization commands before the printjob and a paper-cut command after the printjob).

**Note**: The original version of this software was published in my github repo "circuitpython-picow-escpos" - but since this is not in any way confined to the PicoW, I re-published this software in this repository and continue its development here.

# Software

This circuitpython application uses [circuitpython_toml](https://github.com/elpekenin/circuitpython_toml/), [adafruit_httpserver](https://github.com/adafruit/Adafruit_CircuitPython_HTTPServer/), [adafruit_logging](https://github.com/adafruit/Adafruit_CircuitPython_Logging), [adafruit_minimqtt](https://github.com/adafruit/Adafruit_CircuitPython_MiniMQTT/) and [circuitpython_usyslog](https://github.com/ageagainstthemachine/circuitpython-usyslog) as libraries, they are provided (as copies for convenience, they might need updates at various times in the future) inside the "lib" folder and are all published under the MIT license.

Documentation for configuring the application is [in the Wiki](https://github.com/juergenpabel/circuitpython-escpos-server/wiki/Configuration).

**For USB-connected printers USB-host support in CircuitPython is required** (which for the PicoW is CircuitPython 9.0.0-beta.1 or newer).

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

- Which circuitpython version for PicoW? As of 2024-02-26: [CircuitPython 9.0.0-beta.2](https://circuitpython.org/board/raspberry_pi_pico_w/) is the newest (but ...beta.1 will also work)
  
- Why not provide the libs as MPYs for better performance and reduced memory consumption? Because CircuitPython 9 is still in beta and for the PicoW (my personal setup) it needs a BETA build, which are incompatible with the released MPYs of the other projects.

- I am on a PicoW and use a configuration (settings.toml) much like you describe here but keep getting a `MemoryError` upon startup, what's going on? It's probably the adafruit_minimqtt implementation (together will all the other code) that causes this. What I did: get a copy of the circuitpython repository (`git clone https://github.com/adafruit/circuitpython.git`), than checkout the version that matches your deployed firmware version (`git checkout 9.0.0-beta.2` or whatever) and run the MPY compiler on each the .py files in the src/lib/adafruit_minimqtt directory (like `./mpy-cross/mpy-cross ~/Git/circuitpython-escpos-server/src/lib/adafruit_minimqtt/adafruit_minimqtt.py` and such). This should generate equally named .mpy files that can than be copied into lib/adafruit_minimqtt on your PicoW (delete the .py files). Because of the optimized nature (they are pre-compiled) of those files, circuitpython should now have enough memory to run the app. And if not, repeat with other .py files on the PicoW (until success).
