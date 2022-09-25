#!/bin/sh
# find all processes matching shruti and kill
ps aux | grep shruti | grep -v grep | awk '{print $2}' | xargs kill -9