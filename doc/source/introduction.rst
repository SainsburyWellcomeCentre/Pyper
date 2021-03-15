Introduction
------------

Pyper is designed to track the path of an object of interest in a live feed
from a camera or a recorded video. This program has been used to track rodents
in a open field maze as well as the retina of mice. The new version of Pyper
also allows you to easily customise the image processing to track different
kind of objects.

The live stream of frames can be generated from a USB or firewire camera
(webcam) or from the camera (normal or NoIR) of the Raspberry Pi.
On the Raspberry Pi, a subclass of the standard PiCamera
object is used to speed-up video acquisition and online processing.

The combination of recording and online position tracking allows the definition
of complex behavioural experiment as the program can send a TTL pulse to an
other computer upon detecting the specimen (e.g. mouse) (for example: in a certain region of
space).

Two other kind or ROIs allow you to measure the video pixel values and process
(e.g. average) them as well as restrict the region of space where the tracking
occurs. Finally, the behaviour of the ROIs is extensible through the ROI manager.

The modules can be used interactively from the python interpreter or through
the provided interfaces.
This program provides both a command line interface and a graphical user
interface. For the CLI, the defaults are saved to a user specific preference
file.

Some basic analysis of the extracted position data is also available.
Recorded videos can also be transcoded and regions extracted by Pyper.