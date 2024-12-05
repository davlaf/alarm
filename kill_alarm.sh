#!/bin/bash

# Find the PID of alarm.py and kill it
PID=$(ps aux | grep '[p]ython3 alarm.py' | awk '{print $2}')

if [ -n "$PID" ]; then
    echo "Killing alarm.py process with PID $PID"
    kill -9 $PID
else
    echo "No running alarm.py process found."
fi