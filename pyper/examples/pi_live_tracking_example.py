from time import time, sleep
from multiprocessing import Process

from pyper.tracking.tracking import Tracker
from pyper.contours.roi import Circle
from pyper.exceptions.exceptions import PyperRuntimeError

try:
    import RPi.GPIO as GPIO
except RuntimeError as e:
    print(e)
    raise PyperRuntimeError()

roi = Circle((85, 175), 30)

threshold = 35
previous_time = time()
refractory_period = 1

ttlPin = 5

GPIO.setmode(GPIO.BCM)
GPIO.setup(ttlPin, GPIO.OUT, initial=GPIO.LOW)


def pi_stim():
    GPIO.output(ttlPin, True)
    sleep(0.5)
    GPIO.output(ttlPin, False)


def rpi_call_back():
    global previous_time
    if time() > (previous_time + refractory_period):
        previous_time = time()
        p = Process(target=pi_stim)
        p.daemon = True
        p.start()

tracker = Tracker(dest_file_path='/home/pi/testTrack.mpg',
                  threshold=threshold, teleportation_threshold=1000,
                  plot=True, fast=False,
                  min_area=50,
                  bg_start=5, track_from=10,
                  track_to=10000,
                  callback=rpi_call_back)
positions = tracker.track(roi=roi, record=True)

GPIO.cleanup(ttlPin)
