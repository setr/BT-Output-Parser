#!/usr/bin/env python
import json
import requests
import re
from collections import defaultdict
from jinja2 import Environment, FileSystemLoader

import pytz
import dateutil.parser

env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('template.html')

class bt:
    def __init__(self):
        self.bat = 0
        self.major = 0
        self.minor = 0
        self.published = "" 

def parse(eventline, dataline):
    def converttime(time):
        timestamp = dateutil.parser.parse(time)
        timezoned = timestamp.astimezone(tz=pytz.timezone('America/Chicago'))
        return timezoned.isoformat()

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

def makehtml():
    with open("bat.html", "wb") as f:
        f.write(template.render(btlist=btdict))


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
    print 'ending read'

def filetest():
    # makes sure parsing works on 
    with open('tmp.txt') as f:
        for line in f:
            if line and "event" in line:
                eventline = line
                dataline = next(f)
                parse(eventline, dataline)
            makehtml()

btdict = defaultdict(bt)
stream = 'https://api.particle.io/v1/devices/events?access_token=9b3de52ac7981f0af0fa0972b1a6a130ba747aa8'
#filetest()
readparticle(stream)

