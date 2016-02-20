#!/usr/bin/python

import flask
import collections
import simplejson as json
import time
import requests

app = flask.Flask(__name__)

people = collections.defaultdict(list)

#
# The UUID is a fast-and-lazy key of sorts, make one
# of your own using:
#
# import uuid
# uuid.uuid4()
#
uuid = ''

defaultTemp = 72
awayTemp = 55

saneMin = 55
saneMax = 85

# Slack slackbot hook
slackURL = 'https://mygroup.slack.com/services/hooks/slackbot?token=mytoken&channel=%23hvac'


@app.route("""/%s/<person>/<status>""" % uuid, methods = ['POST'])
def display_pending(person, status):
    now = int(time.time())
    people[person] = { 'status' : status, 'time': now }
    return """ok"""

@app.route("""/%s/status""" % uuid)
def getstatus():
    return """%s""" % json.dumps(people)

@app.route("""/%s/temp""" % uuid, methods = ['GET'])
def getstatustemp():
    return """%s""" % json.dumps({'defaultTemp': defaultTemp, 'awayTemp': awayTemp})

@app.route("""/%s/temp""" % uuid, methods = ['POST'])
def setstatustemp():
    data = flask.request.form
    temp = int(data['text'])
    user = data['user_name']
    if temp > saneMax or temp < saneMin:
        return """Requested temp outside of bounds of %s and %s""" % (saneMin, saneMax)
    else:
        global defaultTemp
        defaultTemp = temp
        poststr = """%s has set temperature to %s""" % (user, temp)
        requests.post(slackURL, poststr)
        return "ok"

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')


