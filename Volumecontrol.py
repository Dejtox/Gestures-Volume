import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

#using of our module
tracker = htm.handDetector(detectionCon=0.7, trackCon=0.9)

#variables to calculate FPS
previous_frame = 0
current_frame = 0
video_capture = cv2.VideoCapture(0)

#variables used to play with sound
currently_used_audio_device = AudioUtilities.GetSpeakers()
interface = currently_used_audio_device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volume.GetMute()
volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]

while True:
    success, Live_img = video_capture.read()
    Live_img = tracker.findHands(Live_img)
    multi_hand_list = tracker.findPosition(Live_img, draw=False)
    vol = 0
    volBar = 400
    volPer = 0

    if len(multi_hand_list) != 0:

        #Position of the thumb[8] and index finger[4] in two dimensions
        x1, y1 = multi_hand_list[4][1], multi_hand_list[4][2]
        x2, y2 = multi_hand_list[8][1], multi_hand_list[8][2]

        cv2.circle(Live_img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(Live_img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
        cv2.line(Live_img, (x1, y1), (x2, y2), (255, 0, 255), 3)

        #distance between fingers
        length = math.hypot(x2-x1, x2-y1)

        #linear interpretation of the maximum and minimum value
        #shown by the spread of fingers (length) and the maximum and minimum volume of the device
        vol = np.interp(length, [100, 250], [minVol, maxVol])

        #Frame size
        volBar = np.interp(length, [125, 200], [400, 150])
        #Frame size in %
        volPer = np.interp(length, [125, 200], [0, 100])

        volume.SetMasterVolumeLevel(vol, None)

    current_frame = time.time()
    fps = 1 / (current_frame - previous_frame)
    previous_frame = current_frame

    cv2.rectangle(Live_img, (150, 50), (400, 85), (255, 0, 0), 3)
    cv2.rectangle(Live_img, (int(volBar), 50), (400, 85), (255, 0, 0), cv2.FILLED)
    cv2.putText(Live_img, f'Volume: {int(volPer)}%', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)

    cv2.putText(Live_img, f'FPS: {int(fps)}', (10, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)
    cv2.imshow("Volume Gesture", Live_img)
    cv2.waitKey(1)
