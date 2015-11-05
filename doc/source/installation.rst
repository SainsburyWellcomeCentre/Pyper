============
Installation
============

Dependencies
------------
You will need at least:

* opencv 2.4.9.1
* numpy
* skimage
* python-progressbar


Recommended modules
-------------------
These modules are required only for some of Motion_Tracking's modules and won't
be necessary if you do not use these optional features (e.g. the GUI).

:Command line:
    * configobj

:Acquisition:
    * picamera (for the raspberry pi)

:Analysis:
    * scipy

:GUI:
    * pyqt5
    * PyOpenGL


Installation on linux (assuming a debian based distribution)
------------------------------------------------------------

Please note that the GUI will currently not work on the raspberry pi. This is due to a limitation of the video driver supplied by Broadcom. This program uses QtQuick which in turn uses hardware acceleration to minimise the load on the CPU. The current driver does not support this feature. This issue might be solved in the future using EGLFS. Also, the new UP project by Aaeon should not have this issue as it uses an Intel GPU.

Please note, if you use an Ubuntu distribution, Ubuntu removed the PyQt5 bindings for python 2.7 in 14.04 but reintroduced them afterwards. Please ensure that you use a version for which the *python-pyqt5* is available and not only *python3-pyqt5*. You can check this using:

.. code-block:: bash
    
    apt-cache search python-pyqt5


To install the dependencies, run:

.. code-block:: bash

    sudo apt-get update
    sudo apt-get install python-opencv python-skimage python-progressbar python-configobj python-scipy git

Then download the motion tracking program using:
    
.. code-block:: bash
    
    git clone https://serverurl/motionTracking motionTracking


The following will install the additional dependencies for the GUI:

.. code-block:: bash

     sudo apt-get install python-pyqt5 python-opengl python-pyqt5.qtopengl python-pyqt5.qtquick qml-module-qtquick-controls
     
     
Finaly, for the raspberry-pi camera:

.. code-block:: bash

     sudo apt-get install python-picamera

Remember to activate the camera in raspi-config

.. code-block:: bash
    
    sudo raspi-config

Then select camera -> activate
    
Installation on MacOSX (tested on Mavericks)
--------------------------------------------
The installation was tested with homebrew by Christian Niedworok.

Installing Homebrew:
^^^^^^^^^^^^^^^^^^^^
Homebrew is a package manager that allows to install a lot of standard open source software on mac that wouldn't be available otherwise. One of them is OpenCV.

.. important::
    You will need XCode to install Homebrew
    
If you have the OSX 10.10 you can install Xcode from the app store, otherwise you need to go to https://developer.apple.com/xcode/, sign in with your apple account (you may have to register as a developer to do this) and download an earlier version. The last version that runs on OSX 10.9 is Xcode 6.2.

.. note::
    After installation of Xcode make sure you start it, since it will finalize the install upon its first launch. Be advised that downloading and installing Xcode can take considerable time (>30 minutes).
    
Then, you can install homebrew.    

.. code-block:: bash

    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    
the installer will run and probably tell you it will change some user rights. For example: *“The following directories will be made group writable: /user/local/lib”*. It will also probably ask you to confirm with enter and prompt for your admin password.

Now we have to make sure homebrew software is visible to the system. Open a new terminal window, and in there, type:

.. code-block:: bash

    echo $PATH
    
and check whether you can see the following in the output: “/usr/local/sbin” and “/usr/local/bin”

if “/usr/local/bin” is missing, run the following:

.. code-block:: bash

    echo 'export PATH="$PATH:/usr/local/bin"' >> ~/.bash_profile
    
if “/usr/local/sbin” is missing, do the same but replace /usr/local/bin by /usr/local/sbin

Now open another new terminal window, close the other (old) terminals, run the command in the “important” box above and get ready to install openCV and python.

.. important::
    Homebrew will potentially install additional versions of software you might already have on your system. This software will be installed to /usr/local/. To prevent these versions from clashing, run the following command whenever you are working on the terminal and want to use homebrew or a software that has been installed using homebrew: export PATH="/usr/local/bin:$PATH". This will ensure that - during the currently open terminal session - the homebrew versions have precedence over any other potentially installed versions.

Installing openCV with python:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Please note that there is a default python on the mac that should not be modified. Unfortunately for us though, it is quite an old version. So we'll install a new one and use/modify that one.

.. note::
    Be aware that the installation with homebrew may take some time and will use processor resources as it will need to compile software.
    
.. code-block:: bash

    brew tap homebrew/science
    brew install --with-ffmpeg opencv # Option to have codecs support
    brew install python


The following will set up python for package downloads and create an alias called brewPython that will run the python you just installed.

.. code-block:: bash

    mkdir -p ~/Library/Python/2.7/lib/python/site-packages
    echo 'import site; site.addsitedir("/usr/local/lib/python2.7/site-packages")' >> ~/Library/Python/2.7/lib/python/site-packages/homebrew.pth
    echo 'alias brewPython="/usr/local/bin/python"' >> ~/.bash_profile
    

If you want to use this oversion of python from your standard mac "Applications" folder, run:

.. code-block:: bash

   brew linkapps python


The following will now install python dependencies for the motion tracking software:

.. code-block:: bash

    sudo  -E /usr/local/bin/pip install numpy scipy scikit-image python-dateutil
    sudo  -E /usr/local/bin/pip install pyparsing matplotlib image
    sudo  -E /usr/local/bin/pip isntall PyOpenGL progressbar
    
    
Installing the GUI:
^^^^^^^^^^^^^^^^^^^

The Graphical User Interface relies on a graphical library called QT (initially developed by Nokia). To use the GUI, you will need to install this library and its python bindings.

.. caution::
    QT5 with homebrew requires OS X Lion or newer

To install QT via homebrew first open a terminal, ensure proxies and $PATH are set (see above), then copy this:

.. code-block:: bash

    brew install qt5
    brew install PyQt5 --with-python # Installs the bindings for python 2.7 which is necessary for openCV 2
    
    
Finaly download the motion tracking program using:
    
.. code-block:: bash
    
    git clone https://serverurl/motionTracking motionTracking
    

Installation on Windows
-----------------------
Instructions by Andrew Erskine

To install python you can use a science oriented python distribution. Please make sure you download python 2.7
Then to install the dependencies, you can follow the *pip* commands of the MacOS instructions. E.g.:

.. code-block:: Batch
    
    pip install numpy scipy scikit-image python-dateutil pyparsing matplotlib image PyOpenGL progressbar

The core of the program works fine. You just have to install openCV and link it with your version of python:

* Download OPENCV for Windows: http://opencv.org/downloads.html

* Extract the file (automatic) (doesn't have to be Python folder)

* Go to the folder where you extracted OpenCV and find opencv\\build\\python\\<yourversion (e.g. 2.7)>\\<yoursystem (e.g. 64-bit)>\\cv2.pyd

* Copy the cv2.pyd file and put it in C:\\<PythonFolder (e.g. Python27)>\\Lib\\site-packages\\

* Open a python console and check it worked:

.. code-block:: python

   >> import cv2
   >> print cv2.__version__
   
Finaly download the motion tracking program using:
    
.. code-block:: Batch
    
    git clone https://serverurl/motionTracking motionTracking
   
The GUI however should work but has not been tested because the python bindings for QT5 are not provided for python 2.7 on windows. If you would like to use the GUI, you will have to compile pyqt5 for python 2.7. This as not been tested here.
    
