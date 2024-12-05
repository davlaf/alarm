import cv2
import numpy as np
import pygame
from time import sleep
from datetime import time, datetime
import pyudev

def list_cameras() -> dict:
    """
    List all available camera devices and identify their names.
    Returns a dictionary of device indices mapped to their names.
    """
    context = pyudev.Context()
    cameras = {}
    
    for device in context.list_devices(subsystem="video4linux"):
        camera_index = int(device.device_node.split('/')[-1].replace('video', ''))
        camera_name = device.attributes.asstring('name')
        cameras[camera_index] = camera_name
    
    return cameras

def test_camera(index: int) -> bool:
    """
    Test if the camera at the given index can stream video.
    Returns True if the camera works, False otherwise.
    """
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        return False
    
    ret, _ = cap.read()
    cap.release()
    return ret

def select_camera(name: str) -> int:
    """
    Find the first camera index matching the given name that streams video.
    Returns the index if found, otherwise raises an error.
    """
    cameras = list_cameras()
    for index, camera_name in cameras.items():
        if name in camera_name:
            print(f"Testing camera at index {index}: {camera_name}")
            if test_camera(index):
                return index
    raise ValueError(f"No working camera found matching name: {name}")

def calculate_brightness(frame) -> float:
    """
    Calculate the average brightness of the given frame.
    Returns a value between 0 (dark) and 255 (bright).
    """
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return np.mean(gray_frame)

# Find the camera
try:
    camera_index = select_camera("HD Pro Webcam C920")
    print(f"HD Pro Webcam C920 found and working at index {camera_index}")
except ValueError as e:
    print(str(e))
    exit(1)

# Initialize the webcam
cap = cv2.VideoCapture(camera_index)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

# Load YOLO model
net = cv2.dnn.readNet("/home/dav/alarm/yolov3.weights", "/home/dav/alarm/yolov3.cfg")
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

def isPersonPresent() -> bool:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        return False

    # Create a blob from the frame and perform forward pass
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    # Loop through all the detected objects
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            
            # If the detected object is a person and confidence is high enough, mark person_detected as True
            if class_id == 0 and confidence > 0.5:  # Class ID 0 is 'person' in COCO dataset
                return True
            
    return False

# Initialize pygame mixer
pygame.mixer.init(buffer=8192)
alarm_sound = pygame.mixer.Sound('/home/dav/alarm/iphone_alarm.wav')
light_sound = pygame.mixer.Sound('/home/dav/alarm/ok_google_turn_on_bedroom_lights.wav')

try:
    while True:
        current_time = datetime.now().time()

        # Grab frame from camera
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            continue

        brightness = calculate_brightness(frame)
        print(f"Brightness: {brightness}")

        # Check if within 7:30 AM to 9:00 AM for light sound and if dark
        if time(7, 30) <= current_time <= time(9, 0):
        # if True:
            if brightness < 70:  # Adjust threshold as needed
                print("It's dark! Playing lights sound.")
                if not pygame.mixer.get_busy():
                    light_sound.play()
                sleep(3)
            else:
                print("Bright enough, stopping lights sound.")
                light_sound.stop()
                sleep(3)

        # Check if within 7:30 AM to 10:30 PM for alarm
        if time(7, 30) <= current_time <= time(22, 30):
            if isPersonPresent():
                print("Person!")
                if not pygame.mixer.get_busy():
                    alarm_sound.play()
            else:
                print("Not person!")
                alarm_sound.stop()

except KeyboardInterrupt:
    print("Stopped by user")

finally:
    cap.release()
    cv2.destroyAllWindows()