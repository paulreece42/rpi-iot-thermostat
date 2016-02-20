# rpi-iot-thermostat
automatic thermostat control from a Raspberry Pi with Robogaia temperature controller module



For use with: http://www.robogaia.com/raspberry-temperature-controller-plate.html

Be sure to follow their installl instructions, although you actually need to use raspi-config to enable i2c now

Use at own risk! This is in testing and should not be used. If you hit a bug and it burns your house down, you never should have been using this.

This GitHub consists of:

- IFTTT Recipe: If you're within X distance of home, or leave that area, curl the presence API and update it
- Presence API: This sits on a server or VM you own and listens for updates from IFTTT
- Thermostat Cron: Sets the temperature accordingly if anyone is home or not


