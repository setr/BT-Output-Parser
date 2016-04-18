#!/usr/bin/env bash

killall curl && python parse.py && curl "https://api.particle.io/v1/devices/events?access_token=9b3de52ac7981f0af0fa0972b1a6a130ba747aa8" >> tmp.txt
