from time import time, sleep
from multiprocessing import Process

from pyper.tracking.tracking import Tracker
from pyper.contours.roi import Circle

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print(
    'Error import RPi.GPIO',
    'Check that module is installed with aptitude install python-rpi.gpio or python3-rpi.gpio',
    'Also, make sure that you are root')

roi = Circle((85, 175), 30)

thrsh = 35
previousTime = time()
refractoryPeriod = 1

ttlPin = 5

GPIO.setmode(GPIO.BCM)
GPIO.setup(ttlPin, GPIO.OUT, initial=GPIO.LOW)

def piStim():
    GPIO.output(ttlPin, True)
    sleep(0.5)
    GPIO.output(ttlPin, False)

def rpiCallBack():
    global previousTime
    if time() > (previousTime + refractoryPeriod):
        previousTime = time()
        p = Process(target=piStim)
        p.daemon = True
        p.start()

tracker = Tracker(destFilePath='/home/pi/testTrack.mpg',
                  threshold=thrsh, teleportationThreshold=1000,
                  plot=True, fast=False,
                  minArea=50,
                  bgStart=5, trackFrom=10,
                  trackTo=10000,
                  callback=rpiCallBack)
positions = tracker.track(roi=roi, record=True)

GPIO.cleanup(ttlPin)
