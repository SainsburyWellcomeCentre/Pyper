.. warning:: Not all video files are indexable, which is requried for seeking (jumping to) a specific frame.
    **For files which cannot be indexed** (e.g. .h264 files acquired with a Raspberry Pi camera),
    the preview is achieved by loading a downscaled
    version of the video in memory before playing it.\\

    This has 2 downsides.:

    #. The video is of lower resolution.
    #. The size of the video is limited by the amount of RAM in the machine.

    **Indexable video files are loaded normally.**
    For large videos with seek information missing, a workaround may be
    to use the *transcoding* tab to export your video to a different format.
    **THIS DOES NOT AFFECT THE TRACKING WHICH ALWAYS LOADS THE VIDEO ONE FRAME AT A TIME.**