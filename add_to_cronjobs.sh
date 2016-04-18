#!/usr/bin/env bash

echo "* 12 * * * root `dirname $0`/wrapper.sh " >> /etc/crontab 
