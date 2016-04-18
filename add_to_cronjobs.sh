#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# starts an initial curl stream
curl "https://api.particle.io/v1/devices/events?access_token=9b3de52ac7981f0af0fa0972b1a6a130ba747aa8" >> $DIR/tmp.txt &

echo "* 12 * * * root $DIR/wrapper.sh " >> /etc/crontab 
