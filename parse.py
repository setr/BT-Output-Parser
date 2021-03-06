#!/usr/bin/env python
import json
import requests
import re
import os
from collections import defaultdict
import pickle

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
picklenum = 0
picklepath = "p_objs/"

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

def savedict():
    # pickle the btdict 
    global picklenum
    picklenum += 1 # constantly increment..
    picklefile = picklepath + str(picklenum) + '.p'
    pickle.dump( btdict, open( picklefile, "wb" ) )

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

def readfile(filename):
    # makes sure parsing works on 
    with open(filename) as f:
        for line in f:
            if line and "event" in line and ("Battery" in line or "Sleep" in line):
                eventline = line
                dataline = next(f)
                parse(eventline, dataline)
    checkbat() # send an email if any bt is under 25% bat, or hasn't been responding
    makehtml() # generate an html table to display bluetooth objects
    savedict() # save the dict to p_objs
    os.remove(filename)


btdict = None
if not os.path.exists(picklepath):
    os.makedirs(picklepath)

# if there's a dict saved, load and use that instead
objs = os.listdir(picklepath)
if objs:
    objs = [re.match('(\d+)\..*', filename).group(1) for filename in objs] 
    picklenum = sorted(map(int, objs), reverse=True)[0]

    picklefile = picklepath + str(picklenum) + '.p'
    btdict = pickle.load( open( picklefile, "rb" ) )
else:
    btdict = defaultdict(bt)

# to read directly from stream
#stream = 'https://api.particle.io/v1/devices/events?access_token=9b3de52ac7981f0af0fa0972b1a6a130ba747aa8'
#readparticle(stream)

# new plan ... curl reads the stream constantly into a file
# python gets executed once a day to read the file
filename = 'tmp.txt'
if os.path.isfile(filename):
    readfile(filename)
else:
    raise Exception('%s is missing, most likely the curl stream died')

