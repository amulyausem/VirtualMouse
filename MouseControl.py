import cv2
import numpy as np
import HandTrackingModule as htm
import time
import autopy
import pyautogui
from subprocess import call

wCam, hCam = 640, 480
frameR = 75   #Frame reduction
smoothening = 7


pTime = 0
plocX, plocY = 0, 0 #Previous location
clocX, clocY = 0, 0 #Current location
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

detector = htm.handDetector(maxHands=1)
wScr, hScr = autopy.screen.size()

while True:
    #Finding the landmarks
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)

    #Get the tip of the index and middle finger
    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]

        #Check which fingers are up
        fingers = detector.fingersUp()
        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR),(255, 0, 255), 2)

        #Only Index Finger Up: Moving Mode
        if fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0:

            #Convert the coordinates
            x3 = np.interp(x1, (frameR, wCam-frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam-frameR), (0, hScr))

            #Smooth Values for better cursor movement
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening

            #Move Cursor
            autopy.mouse.move(wScr - clocX, clocY)
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            plocX, plocY = clocX, clocY

        #Both Index and middle are up: Clicking Mode
        if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0:

            #Finding distance between fingers
            length, img, lineInfo = detector.findDistance(8, 12, img)

            #Click mouse if distance is less than 40
            if length < 40:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                autopy.mouse.click()

        #Only Index Finger Up: Right Click
        if fingers[1] == 0 and fingers[2] == 1 and fingers[3] == 0:
            pyautogui.click(button='right')

        #Only Thumb Finger Up: Scroll Up
        if fingers[0] == 1 and fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0: 
            pyautogui.scroll(10)
            pyautogui.PAUSE=1

        #Only Little Finger Up: Scroll Down
        if fingers[0] == 0 and fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 1: 
            pyautogui.scroll(-10)
            pyautogui.PAUSE=1



    #Display Frame rate
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (28, 58), cv2.FONT_HERSHEY_PLAIN, 3, (255, 8, 8), 3)

    #Display
    cv2.imshow("Image", img)
    cv2.waitKey(1)

