#!/bin/bash

# Download YOLOv3 weights
wget https://pjreddie.com/media/files/yolov3.weights

# Download YOLOv3 configuration file
wget https://github.com/pjreddie/darknet/blob/master/cfg/yolov3.cfg?raw=true -O yolov3.cfg

# Download COCO class names
wget https://github.com/pjreddie/darknet/blob/master/data/coco.names?raw=true -O coco.names
