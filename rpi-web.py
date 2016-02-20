#!/usr/bin/python

import flask

app = flask.Flask(__name__)


import RPi.GPIO as GPIO
import smbus

GPIO.setmode(GPIO.BOARD)
bus = smbus.SMBus(1)

#I2C addres
address = 0x4d

# From http://www.robogaia.com/uploads/6/8/0/9/6809982/robogaia_temperature_controller.tar.gz
def get_fahrenheit_val(): 
    data = bus.read_i2c_block_data(address, 1,2)
    val = (data[0] << 8) + data[1]
    return val/5.00*9.00/5.00+32.00

GPIO.setup(15, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)

@app.route("/")
def dashboard():
    return """Temp: %s <br>Heat On: %s""" % (get_fahrenheit_val(), GPIO.input(15))

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')


