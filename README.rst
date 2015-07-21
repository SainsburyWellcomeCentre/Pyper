.. Motion_Tracking documentation master file, created by
   sphinx-quickstart on Tue Jun  2 19:41:30 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

===========================================
Welcome to Motion_Tracking's documentation!
===========================================


Introduction
------------

This program allows the tracking of mice in open field maze from pre-recorded 
videos or from a live feed. The live stream of frames can be generated from
a usb camera or from the camera (normal or NoIR) of the Raspberry Pi. On the
Raspberry Pi, a subclass of the standard PiCamera object is used to speed-up
video acquisition and online processing.

The combination of recording and online position tracking allows the definition
of complex behavioural experiment as the program can send a TTL pulse to an
other computer upon detecting the mouse (for example: in a certain region of 
space).

The modules can be used interactively from the python interpreter or through
the provided interfaces.
This program provides both a command line interface and a graphical user
interface. For the CLI, the defaults are saved to a user specific preference
file.

Some basic analysis of the extracted position data is also available.
Two classes are also supplied for viewing of the recorded videos or transcoding.

Please see the instructions below for installation and usage.

=======
Example
=======
.. figure:: https://github.com/SainsburyWellcomeCentre/motionTracking/raw/master/doc/source/exampleCapture.gif
    :align: center
    :alt: A usage example of the software
    :figwidth: 500
    
    An example of the tracking software in action.
    
    The yellow square at the bottom right lights up when the mouse enters the
    predefined Region Of Interest (the yellow circle). This behaviour can
    easily be overwritten by the user by specifying a different function.
    

=============
Documentation
=============

For further documentation, you can compile the documentation using sphinx
or alternatively, head to http://www.margrie-lab.com/motionTracking
