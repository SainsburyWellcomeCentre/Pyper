Installation on linux (assuming a debian based distribution)
------------------------------------------------------------

.. note::
    The most recent version of the Raspberry pi video driver should allow for OpenGL accelerated programs
    to run on the X window system. However, this has not been tested with Pyper yet.
    The Raspberry Pi header-compatible UP board by Aaeon uses an Intel GPU and does thus not have this issue.

.. important::
    If you use an Ubuntu distribution, Ubuntu removed the PyQt5 bindings for python 2.7 in 14.04
    but reintroduced them afterwards.
    Please ensure that you use a version for which the *python-pyqt5* is available and not only *python3-pyqt5*.
    You can check this using:

.. code-block:: bash

    apt-cache search python-pyqt5


To install the dependencies, run:

.. code-block:: bash

    sudo apt-get update
    sudo apt-get install python-opencv python-skimage python-dateutil python-pyparsing python-progressbar python-configobj python-scipy git

Then download the motion tracking program using:

.. code-block:: bash

    git clone https://github.com/SainsburyWellcomeCentre/Pyper.git pyper

If you want to use the command line interface, copy the pyper.conf file from the pyper folder
to your home folder preceded by a dot. Assuming Pyper is in your home folder, type the following
command:

.. code-block:: bash

    cp ~/pyper/config/pyper.conf ~/.pyper.conf


The following will install the additional dependencies for the GUI:

.. code-block:: bash

     sudo apt-get install python-pyqt5 python-opengl python-pyqt5.qtopengl python-pyqt5.qtquick
     sudo apt-get install qml-module-qtquick-controls


Finally, for the raspberry-pi camera:

.. code-block:: bash

     sudo apt-get install python-picamera

Remember to activate the camera in raspi-config

.. code-block:: bash

    sudo raspi-config

Then select camera -> activate

Installation on MacOSX (tested on Mavericks)
--------------------------------------------
Installation instructions by Christian Niedworok.

Installing Homebrew:
^^^^^^^^^^^^^^^^^^^^
Homebrew is a package manager that allows to install a lot of standard open source software on mac
 that wouldn't be available otherwise. One of them is OpenCV.

.. important::
    You will need XCode to install Homebrew

If you have the OSX 10.10 you can install Xcode from the app store,
otherwise you need to go to https://developer.apple.com/xcode/, sign in with your apple account
(you may have to register as a developer to do this) and download an earlier version.
The last version that runs on OSX 10.9 is Xcode 6.2.

.. note::
    After installation of Xcode make sure you start it, since it will finalize the install upon its first launch.
    Be advised that downloading and installing Xcode can take considerable time (>30 minutes).

Then, you can install homebrew.

.. code-block:: bash

    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

The installer will run and probably tell you it will change some user rights.
For example: *“The following directories will be made group writable: /user/local/lib”*.
It will also probably ask you to confirm with enter and prompt for your admin password.

Now we have to make sure homebrew software is visible to the system. Open a new terminal **window**, and in there, type:

.. code-block:: bash

    echo $PATH

and check whether you can see both of the following in the output: “/usr/local/sbin” and “/usr/local/bin”

if “/usr/local/bin” is missing, run the following:

.. code-block:: bash

    echo 'export PATH="$PATH:/usr/local/bin"' >> ~/.bash_profile

if “/usr/local/sbin” is missing, do the same but replace /usr/local/bin by /usr/local/sbin

Now open another new terminal window, close the other (old) terminals,
run the command in the “important” box below and get ready to install openCV and python.

.. important::
    Homebrew will potentially install additional versions of software you might already have on your system.
    This software will be installed to /usr/local/.
    To prevent these versions from clashing, run the following command whenever you are working on the terminal
    and want to use homebrew or a software that has been installed using homebrew.
    This will ensure that - during the currently open terminal session - the homebrew versions have precedence
    over any other potentially installed versions.

.. code-block:: bash

    export PATH="/usr/local/bin:$PATH"

Installing openCV with python:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Please note that there is a default python on the mac that should not be modified.
Unfortunately for us though, it is quite an old version. So we'll install a new one and use/modify that one.

.. note::
    Be aware that the installation with homebrew may take some time and will use processor resources
     as it will need to compile software.

.. code-block:: bash

    brew tap homebrew/science
    brew install --with-ffmpeg opencv # Option to have codecs support
    brew install python


The following will set up python for package downloads and create an alias called brewPython
 that will run the python you just installed.

.. code-block:: bash

    mkdir -p ~/Library/Python/2.7/lib/python/site-packages
    echo 'import site; site.addsitedir("/usr/local/lib/python2.7/site-packages")' >> ~/Library/Python/2.7/lib/python/site-packages/homebrew.pth
    echo 'alias brewPython="/usr/local/bin/python"' >> ~/.bash_profile


If you want to use this version of python from your standard mac "Applications" folder, run:

.. code-block:: bash

   brew linkapps python


The following will now install python dependencies for Pyper:

.. code-block:: bash

    sudo  -E /usr/local/bin/pip install numpy scipy scikit-image python-dateutil
    sudo  -E /usr/local/bin/pip install pyparsing matplotlib image
    sudo  -E /usr/local/bin/pip install PyOpenGL progressbar configobj

Installing the GUI:
^^^^^^^^^^^^^^^^^^^

The Graphical User Interface relies on a graphical library called QT (initially developed by Nokia).
To use the GUI, you will need to install this library and its python bindings.

.. caution::
    QT5 with homebrew requires OS X Lion or newer

To install QT via homebrew first open a terminal, ensure proxies and $PATH are set (see above), then copy this:

.. code-block:: bash

    brew install qt5
    brew install PyQt5 --with-python # Installs the bindings for python 2.7 which is necessary for openCV 2


Getting the program
^^^^^^^^^^^^^^^^^^^
Finally download the motion tracking program using:

.. code-block:: bash

    git clone https://github.com/SainsburyWellcomeCentre/Pyper.git pyper

If you want to use the command line interface, copy the pyper.conf file from the pyper folder
to your home folder preceded by a dot. Assuming pyper is in your home folder, type the following
command:

.. code-block:: bash

    cp ~/pyper/config/pyper.conf ~/.pyper.conf

At the end if the program doesn't start, try running:

.. code-block:: bash

    brew update
    brew upgrade
    brew doctor

This should let you know if there are any issues with your homebrew installation.
It might be that homebrew is asking you to link some libraries. If so follow the instructions on screen.
Ensure that /usr/loca/lib is writeable.

.. code-block:: bash

    ls -l /usr/loca/lib

Installation on Windows
-----------------------
Instructions by Andrew Erskine

To install python you can use a science oriented python distribution. Please make sure you download python 2.7
Then to install the dependencies, you can follow the *pip* commands of the MacOS instructions. E.g.:

.. code-block:: Batch

    pip install numpy scipy scikit-image python-dateutil pyparsing matplotlib image PyOpenGL progressbar configobj

The core of the program works fine. You just have to install openCV and link it with your version of python:

* Download OPENCV for Windows: http://opencv.org/downloads.html

* Extract the file (automatic) (doesn't have to be Python folder)

* Go to the folder where you extracted OpenCV and find
  opencv\\build\\python\\<yourversion (e.g. 2.7)>\\<yoursystem (e.g. 64-bit)>\\cv2.pyd

* Copy the cv2.pyd file and put it in C:\\<PythonFolder (e.g. Python27)>\\Lib\\site-packages\\

* Open a python console and check it worked:

.. code-block:: python

   >>> import cv2
   >>> print cv2.__version__

Finally download pyper:

.. code-block:: Batch

    git clone https://github.com/SainsburyWellcomeCentre/Pyper.git pyper

If you want to use the command line interface, copy the pyper.conf file from the pyper/config folder
to your home folder preceded by a dot.

.. warning::
    Although the GUI should work, it has not been tested because the python bindings for QT5
    are not provided for python < 3 on windows.
    If you would like to use the GUI, you will have to compile pyqt5 for python 2.7.
    Although there is no reason to believe this would not work, this has not been tested here.