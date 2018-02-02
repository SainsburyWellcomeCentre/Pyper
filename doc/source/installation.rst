============
Installation
============

Dependencies
------------
You will need at least:

* opencv 2.4.9.1
* numpy
* scipy
* scikit-image
* configobj
* skimage
* python-dateutil
* progressbar
* ffmpeg
* pyparsing
* matplotlib


Recommended modules
-------------------
These modules are required only for some of Pyper's modules and won't
be necessary if you do not use these optional features (e.g. the GUI).

:Acquisition:
    * picamera (for the raspberry pi)

:GUI:
    * pyqt5.6
    * PyOpenGL

:Documentation:
    * sphinx
    * sphinx-argparse

The default installation method through Anaconda
------------------------------------------------
`Miniconda <https://conda.io/miniconda.html>`__ is a crossplatform python distribution.
It is in widespread use in the scientific community and provides a way to easily install OpenCV2 [opencv]_
FFmpeg [ffmpeg]_ and PyQT5 [qt]_ for python2 in Windows, MacOS and Linux.
Pyper thus now provides an installer based on miniconda to install the required
libraries and the Pyper programm.

The first steps require to:

#. Make sure that you have a good internet connection available and that your computer is connected to a power source.
#. Download and install miniconda python 2.7 64 bits from `<https://conda.io/miniconda.html>`__.
#. Download and unzip `pyper <https://github.com/SainsburyWellcomeCentre/Pyper/archive/master.zip>`__ from github.
#. Open a terminal inside the extracted pyper directory
    .. code-block:: bash

        cd Pyper-master # assuming the folder is called Pyper-master and we are in the parent folder

    .. note:: On windows, one should use the Anaconda Command Prompt for this task.

To run the installer, on Linux or MacOSX, run:

.. code-block:: bash

    bash install_pyper.sh

On Windows, open the install_pyper.bat file in a text editor and copy each line that does not start with **REM**
into the Anaconda Command Prompt. This is necessary because the file execution stops after activating the
environment.


The installation should take a while. After it is done, you must change directory using for example cd .., (so that python does not try to load
the modules from the inzipped file) and then run

MacOS/Linux:

    .. code-block:: bash

        source activate pyper_env
        python -m pyper.gui.tracking_gui

On Windows:

    .. code-block:: bat

        activate pyper_env
        python -m pyper.gui.tracking_gui


Installation without Anaconda
-----------------------------
If you do not wish to use Anaconda you can read the legacy installation instructions below:

.. toctree::
   :titlesonly:

   legacy_installation_instructions
    

-------------------------

.. [qt] The Graphical User Interface relies on a graphical library called QT (initially developed by Nokia).
    The GUI of Pyper is developed using a QT technique called QtQuick which relies on OpenGL.

.. [opencv] The image processing and video input and output relies on OpenCV 2.
    From wikipedia:
    OpenCV (Open Source Computer Vision) is a library of programming functions mainly aimed at real-time computer vision.
    Originally developed by Intel, it was later supported by Willow Garage and is now maintained by Itseez.
    The library is cross-platform and free for use under the open-source BSD license.

.. [ffmpeg] FFmpeg is a library for video input and output used by OpenCV.
    From wikipedia:
    FFmpeg is a free software project that produces libraries and programs for handling multimedia data.
    FFmpeg includes libavcodec, an audio/video codec library used by several other projects, libavformat (Lavf),
    an audio/video container mux and demux library, and the ffmpeg command line program for transcoding
    multimedia files.
    FFmpeg is published under the GNU Lesser General Public License 2.1+ or GNU General Public License 2+
    (depending on which options are enabled).

    The name of the project is inspired by the MPEG video standards group,
    together with "FF" for "fast forward".
