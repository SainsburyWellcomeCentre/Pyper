===============
Troubleshooting
===============

The buttons are grayed out I can't use them
-------------------------------------------
    - The video must be loaded or processed for some functions to become available

The detection doesn't give me any result
----------------------------------------
    - Please check that your sample is in the image during the frame range you are tracking
    - broaden your size restriction and lower your threshold
    - use the diff option and check what the camera is seeing as the diff.
    - Select your threshold based on the previous test.
    - See 'The diff is noisy and there is a lot of background' below for further troubleshooting.


The diff is noisy and there is a lot of background
--------------------------------------------------
    - As the camera will setup/settle at the beginning of the recording
      and the video format may use compression (filtering) in time,
      using the very first frame as reference is usually inadvisable,
      consider using frame >= 5 instead for best results.
    - If the images are noisy, you can consider using more than n=1 for the number of reference frames.
      In that case, the frames will be averaged and the signal n*SD above average used for tracking.
      Please consider using high SD numbers in the case where background is detected.


I performed the tracking but no coordinates appear in the 'Analyse' tab
-----------------------------------------------------------------------
    - Make sure that you select the proper mode (tracking or recording) via the UI tickboxes and select update.
    
I changed some parameters but the tracking is not affected
----------------------------------------------------------
    - The tracking can only run in a non interactive way.
      You need to click the stop button and play again after changing parameters (ref, threshold...)
      except for the type of frame displayed.
    
I see two ROIs
--------------
    - This means you have drawn a new ROI after the tracking. One ROI belongs to the UI, the other to the image.
      If you now press track again, the image ROI will now match the UI ROI.


============
Known issues
============
A list/discussion of known issues and planned features of the program can be found at:
https://github.com/SainsburyWellcomeCentre/Pyper/issues

    
