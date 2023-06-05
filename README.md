# ESP32-Rocket-Base

ESP32 Rocket Base is an open-source launching base for small rockets made by [Space Propulsion Raboratory](https://space-propulsion-laboratory.repl.co/index.php?page=LaunchPad), and it works with:
- 27Ω resistor to ignite the fire
- 12v power supply for the resistor and relay
- ESP32 microcontroller
- 5v power supply for the ESP32
- [MicroPython](https://micropython.org/)

You can made it by yourself at home using our code, and remote controlling the whole base with Bluetooth Low Energy, and the [Serial Bluetooth Terminal](https://play.google.com/store/search?q=serial+bluetooth+terminal&c=apps&pli=1) Android app from your smartphone/tablet

![ESP32 circuit](https://raw.githubusercontent.com/Space-Propulsion-Laboratory/ESP32-Rocket-Base/main/rocket-launchpad-circuit.png)

# Serial commands

You can use some commands via serial bluetooth to control the ESP32:
- launch(any number): programs a launch after x seconds (for example: launch10 programs a launch after 10 seconds
- mem: shows the free memory on the ESP32
- on: turns on the relay
- off: turns off the relay
- startMeasure: shows the values from 2235 to 2545 from a 10K potentiometer connected to the pin 25, recording them in the "measures" file
- stopMeasure: stops the measure of the previous command
