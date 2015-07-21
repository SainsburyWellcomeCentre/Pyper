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

.. code-block:: bash

    sudo apt-get update
    sudo apt-get install python-opencv python-skimage python-progressbar python-configobj python-scipy python-pyqt5 python-opengl git
    git clone https://serverurl/motionTracking motionTracking
    
    
Installation on MacOSX (tested on Mavericks)
--------------------------------------------
The installation was tested with homebrew by Christian Niedworok.

Installing Homebrew:
^^^^^^^^^^^^^^^^^^^^
Homebrew is a package manager that allows to install a lot of standard open source software on mac that wouldn't be available otherwise. One of them is OpenCV.

.. important::
    You will need XCodew to install Homebrew
    
If you have the OSX 10.10 you can install Xcode from the app store, otherwise you need to go to https://developer.apple.com/xcode/, sign in with your apple account (you may have to register as a developer to do this) and download an earlier version. The last version that runs on OSX 10.9 is Xcode 6.2.

.. important::
    Homebrew will potentially install additional versions of software you might already have on your system. This software will be installed to /usr/local/. To prevent these versions from clashing run the following command whenever you are working on the terminal and want to use homebrew or a software that has been installed using homebrew: export PATH="/usr/local/bin:$PATH". This will ensure that - during the currently open terminal session - the homebrew versions have precedence over any other potentially installed versions.
    
Then, you can install homebrew.    

.. code-block:: bash

    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    
the installer will run, probably tell you it will change some user rights (e.g. “The following directories will be made group writable: /user/local/lib”) ask you to confirm with enter and potentially ask for your admin password.

Now we have to make sure homebrew software is visible to the system. Open a new terminal window, and in there, type:

.. code-block:: bash

    echo $PATH
    
and check whether you can see the following in the output: “/usr/local/sbin” and “/usr/local/bin”

if “/usr/local/bin” is missing, run the following:

.. code-block:: bash

    echo 'export PATH="$PATH:/usr/local/bin"' >> ~/.bash_profile
    
if “/usr/local/sbin” is missing, do the same but replace /usr/local/bin by /usr/local/sbin

Now open another new terminal window, close the other (old) terminals, run the command in the “important” box above and get ready to install openCV and python.

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


The following will now install python dependencies for the motion trackig software:

.. code-block:: bash

    sudo  -E /usr/local/bin/pip install numpy scipy scikit-image python-dateutil
    sudo  -E /usr/local/bin/pip install pyparsing matplotlib image
    sudo  -E /usr/local/bin/pip isntall PyOpenGL progressbar
    
    
Installing the GUI:
^^^^^^^^^^^^^^^^^^^

The Graphical User Interface relies on a graphical library called QT (initially devlopped by Nokia). To use the GUI, you will need to install this library and it's python bindings.

To install QT via homebrew first open a terminal, ensure proxies and $PATH are set (see above), then copy this:

.. code-block:: bash

    brew install qt5
    brew install PyQt5 --with-python # Installs the bindings for python 2.7 which is necessary for openCV 2
    








