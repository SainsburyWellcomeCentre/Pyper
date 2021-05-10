from time import time, sleep
from multiprocessing import Process

from pyper.tracking.tracking import Tracker
from pyper.contours.roi import Circle

from pyper.config import conf

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print(
        'Error import RPi.GPIO',
        'Check that module is installed with aptitude install python-rpi.gpio or python3-rpi.gpio',
        'Also, make sure that you are root')

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

tracker = Tracker(params=conf.config, dest_file_path='/home/pi/testTrack.mpg',
                  plot=True, callback=rpi_call_back)  # FIXME: plot and callback are deprecated
positions = tracker.track(roi=roi, record=True)

GPIO.cleanup(ttlPin)
