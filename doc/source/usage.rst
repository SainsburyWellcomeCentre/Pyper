=====
Usage
=====

This software can be used in different ways. You can use the graphical interface, the command line interface (from the terminal) or import the modules from a python interpreter.

Using the Graphical interface:
------------------------------

To use the Graphical interface, start a terminal window and then:

Change your working directory to that of the source of the program (subfolder src). This must fit your installation folder. For example if user rcajal downloaded on the desktop:

.. code-block:: bash
    
    cd ~/Desktop/pyperMotionTracking/src
    
Then actually launch the program:

.. code-block:: bash

    python tracking_gui.py
    
When using the graphical interface, hovering over buttons and other elements should display tooltips explaining what these do.

You are greeted by the *welcome* tab. To navigate between functionalities, please select a corresponding tab on the left.
The *Preview* and *Track* tabs require a video to analyse to be loaded. To do so, use the *file* menu or the standard open shortcut on your platform. The record tab will pop up without a camera attached but will require one to select the path to save the video. The *analysis* tab requires to have performed the tracking or recording step before use.

Please note never input empty parameters in the number fields as these are checked for valid numbers.

The *Preview* tab
^^^^^^^^^^^^^^^^^

The preview tab enables you to have a look at a downscaled version of your video to select your start and end point for the analysis as well as the frame that will serve as a reference. Currently, the reference frame must appear before the data frames. This may change in the future and also a dialog may be added to load a picture to serve as a reference.
You can navigate in your video using the controls on the left of the progress bar at the bottom. Then, when on the desired frame select **Ref**, **Start** or **End** accordingly. An end of -1 corresponds to the end of the file.
It is advised to select a frame that is not the first one (e.g. 5 onwards) for the **Ref** as the camera may take a few frames to adjust some parameters and the video may also alter the very first frames.

The *Track* Tab
^^^^^^^^^^^^^^^

This tab is more advanced. It allows you to Track a specimen in the open field from a pre recorded video. The **Ref**, **Start** and **End** parameters set in the *preview* tab apply to the *Track* tab. 

The parameters below (except the type of frame displayed) will only be taken into account the next time the **track** button is pressed.

You should then set a threshold **Thrsh** for the brightness of you sample in the difference image. You can get an idea for this parameter by using the *diff* option from the drop down menu at the bottom. The **min** and **max** parameters refer the minimum and maximum areas of the sample respectively. These are experessed in pixels^2. The **Mvmt** parameter refers to the maximum displacement **in either dimension** of the specimen between two consecutive frames.

In addition, you can supply a number of frames to average for the reference (starting from the **Ref** frame). If detection is difficult, specifying several reference frames and setting the **Sds** parameter will enable you to use variation in the current frame relative to the standard deviation of the averages.

Finaly, the **Clear** parameter will clear object touching the border of the image, The **Extract** parameter is used if the arena is white on a dark background, this option will automatically detect it as an ROI. Finaly, the **Norm** parameter removes the slight variations in global brightness between frames. it will normalise each frame to the brightness of the reference.
 
The default detection parameter should be appropriate for the example videos.

The drop down menu allows you to select between the type of image (level of processing) you want to display. Please note that this option only applies to the portion of the recording that is being actively tracked, the ignored portion will just be displayed as the source (i.e. *raw*).

Finaly, you can define a region of interest using the yellow circle icon. When the mouse enters this ROI, the program will trigger a callback method. The default method draws a square at the bottom right of the image but this behaviour can be altered by overwritting the callback method in a subclass of the GuiTraker class (see API).

If you cannot detect your sample successfuly, please refer to the troubleshooting section.

The *Record* Tab
^^^^^^^^^^^^^^^^

This tab essentialy reproduces the behaviour of the *Track* tab but for videos that are being recorded through a USB or FireWire camera for example. Before starting you must supply a destination path to save the video. The extension will determine the format. The available formats will dependend on the codecs available to ffmpeg in you installation. In tests, best restults were obtained with .avi and .mpg

The *Calibration* tab
^^^^^^^^^^^^^^^^^^^^^

This menu computes the parameters of the lens used to acquire the videos and once calculated, these parameters will be used automatically to undistort the images in the *Track* and the *Record* tabs.
To use this functionnality, you must provide a folder containing a series (e.g. 10) of images acquired with the same lens and parameters as the video and containing a reference chessboard. A printable template can be found at http://docs.opencv.org/2.4/_downloads/pattern.png which will work with the default parameters.
Once the folder is selected, press **Calibrate** and wait for the calibration to finish. Once done, the controls will become available and allow you to browse through the images used for calibration, the images with the features drawn and the undistorted images. You can also save the camera matrix for reference. In the future, it should become possible to load a calibration file from the *Track* and *Record* tabs.

The *Analyse* tab
^^^^^^^^^^^^^^^^^

This tab provides simple analysis and graphing features as well as the ability to save the list of coordinates.

First select the checkbox that corresponds to the tab you want to analyse. Then, click **Update** and you can finaly save your coordinates and plot graphs of distance made by the specimen between frames and change of directions at each frame. To save the graphs, right click on them and a menu will promt you for a destination path.

Using the Command Line Interface:
---------------------------------

.. automodule:: tracking_cli

.. only :: isSystem

    .. autoprogram:: tracking_cli:parser
        :prog: tracking_cli.py
