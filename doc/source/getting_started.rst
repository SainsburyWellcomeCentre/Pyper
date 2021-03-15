===========
Quick start
===========

This is a quick tutorial to get acquainted with the program and browse its different features.
This tutorial assumes you have already successfully installed Pyper and its dependencies following the
tutorial in the :doc:`installation` section.

Starting the program
^^^^^^^^^^^^^^^^^^^^
To get a quick feel for the software, some example files have been included in the resources folder of the program.

.. include:: starting_pyper.rst


Preview
^^^^^^^
Open a file using the file menu or your platform's shortcut and select the *teleporter.h264* file
in the resources sub-folder of the program (i.e. where you downloaded it with git).
You can now go to the *Preview* tab and navigate through the file.

#. Select a reference frame before the specimen enters the field of view (also usually avoid the very first
    image as the camera is still auto-adjusting).
#. Select a start frame (after the reference) where the target has entered the field of view.
#. Select the end of the tracked portion or leave it as is to select the end of the recording by default.


These frames will be used in the *Track* tab.

.. include:: preview_non_seekable_warning.rst

    
Tracking
^^^^^^^^
You can now navigate to the *Track* tab.
Press the *start tracking* arrow (*play* button) and you should see the video begin to play.
At the beginning, the video should play as the source.
Once the video playback reaches the point that you selected for the beginning of the tracking,
the target should become outlined in red and leave a green line as a trail delineating its trajectory.
You can then select a different image type from the drop down menu at the bottom left of the window
to get a feel for the processing going on in the background. This will also allow you to adjust your threshold and
size parameters.

.. versionadded:: 2.0
    It is now possible to also update the tracking controls (apart from the reference and start frames if they have
    already been passed) and see the result immediately.

.. include:: roi_manager.rst

Analysis
^^^^^^^^
Once the end of the recording is reached, you can proceed to the *Analyse* tab and click **Update**.
The list of coordinates will now appear in the table.
Coordinates of (-1, -1) indicate default coordinates that are selected if:

* The frame is before the beginning of the tracked segment of the recording.
* The specimen could not be found in the field of view with the specified parameters.

If you now click angles and distances two graphs should appear indicating the change of direction at each frame
and the distance made at each frame respectively.
To save the coordinates, select **Save** and provide a destination path.

Recording
^^^^^^^^^
If a camera is plugged in to your computer (or it is a laptop with a built-in webcam), you can try the recording mode.

#. Go to the *Record* tab and select a destination file path. Using the default .avi extension should work in most cases.
    If the output is empty at the end of your recording, try one of the other file formats instead.
#. Select **Ref** = 5 and **Start** = 6.
#. Now stand in front of the camera and try to be as still as possible. Press the record button.
    The video should start to appear.
#. Move slightly to either side, the program should start tracking your movements.

You can now go back to the *Analyse* tab and tick the *Recording* box.
Now click **update** again and do the plots again. These should now show the new data from the recording.

As you can see, the tracking parameters are the same as with the *tracking* tab. The roi also behaves the same.

Calibration
^^^^^^^^^^^
This tab allows you to calibrate your camera lens. Using pictures of a simple chessboard pattern,
you can compute and correct this distortion. This is explained in more detail in the :doc:`usage` section.

Transcoding
^^^^^^^^^^^
This tab allows you to change the encoding (CODEC) of your video as well as extract a range of frames and a region
specified by a ROI. You can also scale the output independently in each axis.
This is sometimes useful for several reasons:

#. Your recording CODEC might not allow frame indexing.
#. Some recording devices create frames with a few pixels of NaN data on the border that confuse most video readers like VLC.
    This can easily be solved by cropping the image using the ROI.
#. Most of your video does not contain useful data and you want to reduce it's size to the interesting region.

For more on the *transcoding* tab, see :doc:`usage`
