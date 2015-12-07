.. Pyper documentation master file, created by
   sphinx-quickstart on Tue Jun  2 19:41:30 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=================================
Welcome to Pyper's documentation!
=================================


Introduction
------------

This program allows the tracking of specimen (e.g. a mouse, a rat ...) in an 
open field maze from pre-recorded videos or from a live feed. The live stream 
of frames can be generated from a USB camera or from the camera (normal or NoIR)
of the Raspberry Pi. On the Raspberry Pi, a subclass of the standard PiCamera 
object is used to speed-up video acquisition and online processing.

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

=======
Example
=======
.. figure:: https://github.com/SainsburyWellcomeCentre/pyper/raw/master/doc/source/exampleCapture.gif
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
or alternatively, head to http://pyper.readthedocs.org/en/latest/

=======
Authors
=======
Charly V Rousseau\ :sup:`1`\ , Antonio Gonzalez\ :sup:`2`\ , Andrew Erskin\ :sup:`3`\ , Christian J Niedworok\ :sup:`1`\ , Troy W Margrie\ :sup:`1`\ .

Author information:
    • \ :sup:`1`\ Margrie lab. Sainsbury Wellcome Centre for Neural Circuits and Behaviour, University College London, London, U.K.
    • \ :sup:`2`\ Burdakov lab. Mill Hill Laboratory, The Francis Crick Institute, London, U.K.
    • \ :sup:`3`\ Schaefer lab. Mill Hill Laboratory, The Francis Crick Institute, London, U.K.

The authors would like to thank Edward F Bracey, Nicholas Burczyk, Julia J Harris, Cornelia Schöne and Mateo Vélez-Fort for their useful comments about the interface design and the user instructions.

=======
Licence
=======
| The software in this repository is licensed under the GNU General Public License, version 2 http://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html.
| The graphic assets (under resources/icons or resources/images) are distributed under a Creative commons Attribution-ShareAlike 4.0 International licence (CC BY-SA 4.0) http://creativecommons.org/licenses/by-sa/4.0/legalcode.
