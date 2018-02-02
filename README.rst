=================================
Welcome to Pyper's documentation!
=================================

News : Pyper v2 is here.
------------------------
.. figure:: https://github.com/SainsburyWellcomeCentre/pyper/raw/dev/doc/source/track_tab_ui.png
    :align: center
    :alt: UI of Pyper
    :figwidth: 500

This new version draws on user feedback to implement most of the requested features.

What's new:
    -  New goodies:
        - A new *transcoding* tab to fix broken videos, extract parts of and scale the video.
        - A new ROI system with the ability to select the shape of the ROI, and it's color
        - New ROI functions: measure video values and spatially restrict tracking.
        - A new plugin system for tracking methods. Also adds pupil tracking.
        - Live update of the tracking parameters. If you change the parameters in the GUI they are immediately
          taken into account.
        - Tracking visible even when nothing is found. This helps fine tune the parameters.
    - Behind the scenes:
        - Refactors python code to PEP8 compliance.
        - Major refactoring of the GUI code.
    - Various bug fixes.

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
other computer upon detecting the mouse (for example: in a certain region of
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

=======
Example
=======
.. figure:: https://github.com/SainsburyWellcomeCentre/pyper/raw/dev/doc/source/example_capture.gif
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
Charly V Rousseau\ :sup:`1`\ , Antonio Gonzalez\ :sup:`2`\ , Stephen Lenzi :sup:`1`\ ,
Andrew Erskin\ :sup:`3`\ , Christian J Niedworok\ :sup:`1`\ , Troy W Margrie\ :sup:`1`\ .

Author information:
    • \ :sup:`1`\ Margrie lab. Sainsbury Wellcome Centre for Neural Circuits and Behaviour, University College London, London, U.K.
    • \ :sup:`2`\ Burdakov lab. Mill Hill Laboratory, The Francis Crick Institute, London, U.K.
    • \ :sup:`3`\ Schaefer lab. Mill Hill Laboratory, The Francis Crick Institute, London, U.K.

The authors would like to thank Edward F Bracey, Nicholas Burczyk, Julia J Harris, Cornelia Schöne and Mateo Vélez-Fort
for their useful comments about the interface design and the user instructions.

============
Contributing
============
Contributions to Pyper are welcome.
You can contribute in different ways (with various levels or programing skills required):

- Improving this documentation
- Suggesting features
- Submitting bug reports
- Improving the software directly by doing pull requests

=======
Licence
=======
| The software in this repository is licensed under the GNU General Public License,
  version 2 http://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html.
| The graphic assets (under resources/icons or resources/images)
  are distributed under a Creative commons Attribution-ShareAlike 4.0 International licence (CC BY-SA 4.0)
  http://creativecommons.org/licenses/by-sa/4.0/legalcode.
