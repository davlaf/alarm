#!/bin/bash

# Run the Python script in the background and discard logs
nohup python3 alarm.py > /dev/null 2>&1 &
echo "Alarm script is running in the background with PID $!"