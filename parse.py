#!/usr/bin/env python
import json
import requests
import re
from collections import defaultdict

# for templating
from jinja2 import Environment, FileSystemLoader

# for handling dates
import pytz
import dateutil.parser
import datetime

# for mail
import smtplib
from email.mime.text import MIMEText



env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('template.html')

class bt:
    def __init__(self):
        self.bat = 0
        self.major = 0
        self.minor = 0
        self.published = "" 

def parse(eventline, dataline):
    if "Battery Status" in eventline:
        kosher = dataline[6:]
        data = json.loads(kosher)

        bat = data['data']
        bat = int(re.match('(\d+)', bat).group(1))
        coreid = data['coreid']
        btdict[coreid].bat = bat
        btdict[coreid].published = converttime(data['published_at'])

    elif "System Going to Sleep" in eventline:
        kosher = dataline[6:]
        data = json.loads(kosher)

        stuff = data['data'].split('-')
        major = int(stuff[1])
        minor = int(stuff[3])
        coreid = data['coreid']
        btdict[coreid].published = converttime(data['published_at'])

        btdict[coreid].major = major 
        btdict[coreid].minor = minor 

def converttime(time):
    timestamp = dateutil.parser.parse(time)
    timezoned = timestamp.astimezone(tz=pytz.timezone('America/Chicago'))
    return timezoned.isoformat()

def makehtml():
    with open("bat.html", "wb") as f:
        f.write(template.render(btlist=btdict))
def checkbat():
    for coreid, bt in btdict.items():
        # if it's actually a complete object
        if bt.bat and bt.major and bt.minor and bt.published:
            if bt.bat < 25:
                body = """BAT IS LOW
                CoreID: %s,
                Major: %d,
                Minor: %d,
                Battery: %d%%""" % (coreid, bt.major, bt.minor, bt.bat)
                sendmail(body)

            tz = pytz.timezone('America/Chicago')
            now = datetime.datetime.now(tz)
            then = dateutil.parser.parse(bt.published)
            if now - then > datetime.timedelta(hours=25): #been more than 1 day since last publish
                body = """ No Response
                CoreID: %s,
                Major: %d,
                Minor: %d""" % (coreid, bt.major, bt.minor)
                sendmail(body)

def sendmail(body):
    # Open a plain text file for reading.  For this example, assume that
    # the text file contains only ASCII characters.
    # Create a text/plain message
    print "sending mail"
    msg = MIMEText(body)
    # me == the sender's email address
    # you == the recipient's email address
    me = 'iitlocationserver@gmail.com'
    you = 'bnandaku@iit.edu'
    msg['Subject'] = 'BT Issue'
    msg['From'] = me
    msg['To'] = you
    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
    smtpObj.ehlo()
    smtpObj.starttls()
    smtpObj.login(me, 'a9940047928')
    smtpObj.sendmail(me, [you], msg.as_string())
    smtpObj.quit()


def readparticle(s):
    #r = requests.get('https://api.particle.io/v1/devices/events?access_token=9b3de52ac7981f0af0fa0972b1a6a130ba747aa8', stream=True)
    print 'starting read'
    r = requests.get(s, stream=True)
    for line in r.iter_lines():
        if line and "event" in line and ("Battery" in line or "Sleep" in line):
            eventline = line
            dataline = next(r.iter_lines())
            parse(eventline, dataline)
            makehtml()
            checkbat()
    print 'ending read'

def filetest():
    # makes sure parsing works on 
    with open('tmp.txt') as f:
        for line in f:
            if line and "event" in line and ("Battery" in line or "Sleep" in line):
                eventline = line
                dataline = next(f)
                parse(eventline, dataline)
                makehtml()
                checkbat()

btdict = defaultdict(bt)
stream = 'https://api.particle.io/v1/devices/events?access_token=9b3de52ac7981f0af0fa0972b1a6a130ba747aa8'
filetest()
readparticle(stream)

