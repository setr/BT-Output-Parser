#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

killall curl && python parse.py && curl "https://api.particle.io/v1/devices/events?access_token=9b3de52ac7981f0af0fa0972b1a6a130ba747aa8" >> tmp.txt
