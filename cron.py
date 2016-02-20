#!/usr/bin/python

import smbus
import time
import requests
import RPi.GPIO as GPIO
import logging
import rrdtool

#
# Tunables
#

# Maximum time a person can be idle before ignoring them
max_person_idle = 86400

# Slack slackbot hook
slackURL = 'https://mygroup.slack.com/services/hooks/slackbot?token=mytoken&channel=%23hvac'

# UUID from presence-api.py
uuid = ''

# URL that goes to presence-api.py
presURL = 'http://myserver.com:5000'

# Variance in temperature allowed

variance = 3

# Init GPIO

GPIO.setmode(GPIO.BOARD)

#
# Individual mileage may vary here
# RoboGaia said the SMBus was 1, but in mine
# it was 0
#
bus = smbus.SMBus(1)

#I2C addres
address = 0x4d

GPIO.setup(15, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='/var/log/thermostat.log')


def slack_say(slackstr):
    return requests.post(slackURL, slackstr)

# From http://www.robogaia.com/uploads/6/8/0/9/6809982/robogaia_temperature_controller.tar.gz
def get_fahrenheit_val(): 
	data = bus.read_i2c_block_data(address, 1,2)
	val = (data[0] << 8) + data[1]
	return val/5.00*9.00/5.00+32.00

def heat_on():
    GPIO.output(15, GPIO.HIGH)

def cold_on():
    GPIO.output(13, GPIO.HIGH)

def all_off():
    GPIO.setup(13, GPIO.OUT)
    GPIO.setup(15, GPIO.OUT)
    GPIO.output(13, GPIO.LOW)
    GPIO.output(15, GPIO.LOW)


# Credit goes to http://stackoverflow.com/questions/24101524/finding-median-of-list-in-python
def median(lst):
    lst = sorted(lst)
    if len(lst) < 1:
            return None
    if len(lst) %2 == 1:
            return lst[((len(lst)+1)/2)-1]
    else:
            return float(sum(lst[(len(lst)/2)-1:(len(lst)/2)+1]))/2.0

myTempList = []

for i in range(0,10):
    myTempList.append(get_fahrenheit_val())
    time.sleep(1)

myTemp = median(myTempList)

try:
    r = requests.get("""%s/%s/temp""" % (presURL, uuid))
except:
    all_off()
    try:
        slack_say("Exception, failing all off")
    except:
        pass

defaultTemp = r.json()['defaultTemp']
awayTemp = r.json()['awayTemp']

r = requests.get("""%s/%s/status""" % (presURL, uuid))

people = r.json()

someoneHome = False

for person in people:
    if people[person]['status'] == "entered":
        if time.time() - people[person]['time'] < max_person_idle:
            someoneHome = True


if someoneHome:
    setTemp = defaultTemp
else:
    setTemp = awayTemp


if myTemp < setTemp - variance:
    logging.info("""Temperature is %s, turning heat on""" % myTemp)
    heat_on()
elif myTemp >= setTemp + variance:
    logging.info("""Temperature has reached %s, shutting off""" % myTemp)
    all_off()
else:
    logging.debug("""Temperature is %s, doing nothing""" % myTemp)


rrdtool.update('/opt/temp.rrd', """N:%s:%s:%s""" % (myTemp, GPIO.input(15), GPIO.input(13)))

