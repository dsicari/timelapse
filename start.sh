#!/bin/bash
/home/pi/mjpg_streamer/streamer.sh start
cd /home/pi/timelapse && python3 main.py
