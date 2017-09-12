News : Pyper v2 is here.
------------------------

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