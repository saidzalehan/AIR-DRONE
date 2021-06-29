# The libraries that need to install to run this program
from djitellopy import tello
from pyzbar.pyzbar import decode
from time import sleep
import numpy as np
import cv2
# Install Pygame libraries to run KeyPressModule
# Module that have been create to execute emergency button using keyboard, check python file name KeyPressModule.py
import KeyPressModule as Kpm

Kpm.init()

# Connect the Drone
airDrone = tello.Tello()
airDrone.connect()
print("Battery : " + str(airDrone.get_battery()))
airDrone.streamon()  # To stream the Drone Camera

# Object Detection File
classFile = 'coco.names'
classNames = []
with open(classFile, 'rt') as f:
    classNames = f.read().rstrip('\n').split('\n')
# print(classNames)
# print(len(classNames))

# Read the model
# Download yolov3 file in https://pjreddie.com/darknet/yolo/
# For small fps file but less accuracy Yolotiny ( good for drone )
# For more fps and more accuracy download this file ( Good for more powerful device with highest RAM and GPU )
# Download yolov3.cfg and yolov3.weights
modelCfg = 'yolov3.cfg'
modelWeight = 'yolov3.weights'
# modelCfg = 'yolov3-tiny.cfg'
# modelWeight = 'yolov3-tiny.weights'
net = cv2.dnn.readNetFromDarknet(modelCfg, modelWeight)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)


def fly():
    #airDrone.takeoff()
    hover()
    airDrone.send_rc_control(0, 0, 0, 0)
    hover()
    # airDrone.send_rc_control(0, 0, -50, 0)
    # hover()

    return


# Drone will be static for a moment to get balance
def hover():
    sleep(2)
    airDrone.send_rc_control(0, 0, 0, 0)
    sleep(2)
    return


def scanning():
    airDrone.send_rc_control(0, 0, 0, 0)
    sleep(5)
    airDrone.send_rc_control(0, 0, 0, 0)
    sleep(2)
    return


def land():
    airDrone.send_rc_control(0, 0, 0, 0)
    sleep(2)
    airDrone.land()
    return


# This function will ask the user where to go
def launch():
    print("-----WELCOME TO AIR Drone System-----")
    print("1. Yes")
    print("2. No")
    option = input(" READY TO LAUNCH? : ")

    return option


# Start the drone to fly
def start():
    ready = launch()

    if ready == "1":
        sleep(1)
        fly()
    elif ready == "2":
        print("\n Exit the program......")
        quit()
    else:
        print("\n Invalid Input")
        start()

    return ready


# This function is use to read the qr and turn into String
def qr_code(data):
    qr = ""
    qrc = False
    img = airDrone.get_frame_read().frame  # Reads video from drone camera

    # Makes the QR code content into a String
    for barcode in decode(img):
        qr += barcode.data.decode('ascii')
        print(qr)

    if data == qr:
        qrc = True

    return qrc


# Drone will get the qr and drive the drone
# 2 option to move the drone
# - Use the rc control (LeftRight, ForwardBack, UpDown, XY)
# - Use the basic command like move_forward(cm)
def get_qr_input(ready_to_launch):
    airDrone.send_rc_control(0, 0, 0, 0)
    if ready_to_launch == "1":
        if qr_code("Go"):
            airDrone.move_forward(150)
            hover()
        elif qr_code("CW"):
            airDrone.rotate_clockwise(90)
            hover()
            # airDrone.move_forward(100)
            # hover()
        elif qr_code("Checkpoint 2"):
            airDrone.rotate_clockwise(90)
            hover()
            airDrone.move_forward(50)
            hover()
        elif qr_code("Checkpoint 3"):
            airDrone.rotate_counter_clockwise(90)
            hover()
            airDrone.move_forward(50)
            hover()
        elif qr_code("Scanning"):
            airDrone.rotate_clockwise(90)
            hover()
            scanning()
            airDrone.move_forward(30)
            hover()
        elif qr_code("Land"):
            land()
            airDrone.land()

    return


def find_objects(outputs, img):
    ht, wt, ct = img.shape
    bbox = []
    classids = []
    confs = []
    for output in outputs:
        for det in output:
            scores = det[5:]
            classid = np.argmax(scores)
            confidence = scores[classid]
            if confidence > 0.5:
                w, h = int(det[2] * wt), int(det[3]*ht)
                x, y = int((det[0] * wt) - w / 2), int((det[1]*ht) - h / 2)
                bbox.append([x, y, w, h])
                classids.append(classid)
                confs.append(float(confidence))
    # print(len(bbox))

    indices = cv2.dnn.NMSBoxes(bbox, confs, 0.5, 0.3)

    for i in indices:
        i = i[0]
        box = bbox[i]
        x, y, w, h = box[0], box[1], box[2], box[3]
        # print(x,y,w,h)
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 255), 2)
        cv2.putText(img, f'{classNames[classids[i]].upper()} {int(confs[i] * 100)}%',
                    (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)


def emergency_button():
    if Kpm.getKey("l"):
        airDrone.land()
        sleep(3)


go = start()

while True:
    cap = airDrone.get_frame_read().frame

    cap = cv2.resize(cap, (675, 450))  # Resize the windows
    # cap = cv2.flip(cap, 0)  # to flip the camera because using mirror

    q = ""
    for r in decode(cap):
        q += r.data.decode('ascii')
        cv2.putText(cap, str(r.data.decode('ascii')), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2,
                    (255, 0, 0), 3)

    blob = cv2.dnn.blobFromImage(cap, 1 / 255, (320, 320), [0, 0, 0], 1, crop=False)
    net.setInput(blob)
    layersNames = net.getLayerNames()
    outputNames = [(layersNames[i[0] - 1]) for i in net.getUnconnectedOutLayers()]
    out = net.forward(outputNames)
    find_objects(out, cap)

    cv2.imshow('AIR Drone', cap)
    cv2.waitKey(1)

    get_qr_input(go)
    emergency_button()
    sleep(0.05)
