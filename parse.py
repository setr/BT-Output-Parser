#!/usr/bin/env python
import json
import requests
import re
from collections import defaultdict

def btinit():
    return bt()
class bt:
    def __init__(self):
        self.bat = 0
        self.major = 0
        self.minor = 0

def parse(eventline, dataline):
    if "Battery Status" in eventline:
        print "BT STATUS"
        kosher = dataline[6:]
        data = json.loads(kosher)

        bat = data['data']
        bat = int(re.match('(\d+)', bat).group(1))
        coreid = data['coreid']
        btdict[coreid].bat = bat
        print eventline
        print dataline

    elif "System Going to Sleep" in eventline:
        print "SLEEP"
        print eventline
        kosher = dataline[6:]
        data = json.loads(kosher)

        stuff = data['data'].split('-')
        major = int(stuff[1])
        minor = int(stuff[3])
        coreid = data['coreid']

        btdict[coreid].major = major 
        btdict[coreid].minor = minor 
        print 'MAJOR:', major
        print 'MINOR:', minor

def readparticle(s):
    #r = requests.get('https://api.particle.io/v1/devices/events?access_token=9b3de52ac7981f0af0fa0972b1a6a130ba747aa8', stream=True)
    print 'starting read'
    r = requests.get(s, stream=True)
    for line in r.iter_lines():
        if line and "event" in line and ("Battery" in line or "Sleep" in line):
            eventline = line
            dataline = next(r.iter_lines())
            parse(eventline, dataline)

            for coreid, bt in btdict.items():
                print "coreid", coreid
                print "major:", bt.major
                print "minor:", bt.minor
                print "bat:" , bt.bat
    print 'ending read'

def filetest():
    # makes sure parsing works on 
    with open('tmp.txt') as f:
        for line in f:
            if line and "event" in line:
                eventline = line
                dataline = next(f)
                parse(eventline, dataline)



btdict = defaultdict(bt)
stream = 'https://api.particle.io/v1/devices/events?access_token=9b3de52ac7981f0af0fa0972b1a6a130ba747aa8'
filetest()
readparticle(stream)

