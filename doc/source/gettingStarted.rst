===========
Quick start
===========

Starting the program
^^^^^^^^^^^^^^^^^^^^
To get a quick feel for the software, some example files have been included in the resources folder of the program.
Start by opening the program, in a terminal:

Change your working directory to that of the source of the program (subfolder src). This must fit your installation folder. For example if user rcajal downloaded on the desktop:

.. code-block:: bash
    
    cd ~/Desktop/motionTracking/src
    
Then actually launch the program:

.. code-block:: bash

    python tracking_gui.py
    
.. note::
    You may want to use brewPython if you followed the mac instructions or a full path on windows
        
The graphical interface should now be started.

Preview
^^^^^^^
Open a file using the file menu or your platform shortcut and select the *teleporter.h264* file in the resources subfolder of the program (i.e. where you downloaded it with git).
You can now go to the *Preview* tab and navigate through the file.

* Select a reference frame before the specimen enters the arena (also avoid the very first image).
* Select a start frame (after the reference) where the mouse has entered the arena.
* Select the end of the tracked portion or leave it as is to select the end of the recording by default.
    
Tracking
^^^^^^^^
You can now navigate to the *Track* tab.
Press the *start tracking* arrow (*play* button) and you should see the video begin to play. At the beginning, the video should play as the source. Note that the resolution is better than in the preview because the preview is downscaled. Once the video playback reaches the point that you selected for the beginning of the tracking, the mouse should become outlined in red and leave a green line as a trail delineating its trajectory. You can then select a different image type from the drop down menu at the bottom of the window to get a feel for the processing going on in the background.

Analysis
^^^^^^^^
Once the end of the recording is reached, you can proceed to the *Analyse* tab and click **Update**. The list of coordinates will now appear in the table. Coordinates of (-1, -1) indicate default coordinates that are selected if:

* The frame is before the beginning of the tracked segment of the recording.
* The specimen could not be found in the arena with the specified parameters.

If you now click angles and distances two graphs should appear indicating the change of direction at each frame and the distance made at each frame respecively. To save the coordinates, select **Save** and provide a destination path.

Recording
^^^^^^^^^
If a camera is plugged in to your computer (or it is a laptop with a built-in webcam), you can try the recording mode.

* Go to the *Record* tab and select a destination file path. Using the default .avi extension should work in most cases. If the output is empty at the end of your recording, try one of the other file formats instead.
* Select **Ref** = 5 and **Start** = 6.
* Now stand in front of the camera and try to be as still as possible. Press the record button. The video should start to appead.
* Move slightly to either side, the program should start tracking your movements.

You can now go back to the *Analyse* tab and tick the *Recording* box. Now click **update** again and do the plots again. These should now show the new data from the recording.
