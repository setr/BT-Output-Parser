#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "* 12 * * * root $DIR/wrapper.sh " >> /etc/crontab 
