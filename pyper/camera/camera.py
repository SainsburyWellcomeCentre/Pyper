import platform
is_pi = (platform.machine()).startswith('arm')
if is_pi:
    from picamera.camera import PiCamera, PiCameraRuntimeError
"""
*****************
The camera module
*****************

This module only hosts the CvPiCamera class
This class is meant for fast acquisition of frames from a Raspberry Pi
camera for openCV processing


:author: crousse
"""

if is_pi:
    class CvPiCamera(PiCamera):
        """
        A subclass of picamera that keeps a reference of its encoder and doesn't close it between frames.
        This speeds up the acquisition process substantially.

        .. note:: This class is meant to acquire in format 'bgr' (for openCV)

        """

        def __init__(self):
            """
            Initialises the camera and sets the isFirstFrame attribute to allow
            creation of the encoder on first frame only
            """
            PiCamera.__init__(self)
            self.isFirstFrame = True

        def _init_encoder(self):
            """Creates the 'bgr' encoder to be reused for each frame. To be used for first frame only."""
            self.splitter_port = 0
            use_video_port = True
            fmt = 'bgr'
            resize = None
            with self._encoders_lock:
                camera_port, output_port = self._get_ports(use_video_port, self.splitter_port)
            encoder = self._get_image_encoder(camera_port, output_port, fmt, resize)
            self.encoder = encoder
            self._encoders[self.splitter_port] = encoder

        def close_encoder(self):
            """Closes self.encoder and deletes the encoder from self._encoders"""
            self.encoder.close()
            with self._encoders_lock:
                del self._encoders[self.splitter_port]

        def quick_capture(self, output):  # resize=None
            """
            A method similar to the standard capture except it reuses the encoder

            :param output: The stream to write to (the frame gets written to stream.array)
            :type output: picamera.array.PiRGBArray
            :raises PiCameraRuntimeError: if timeout occurs
            """
            if self.isFirstFrame:
                self._init_encoder()
                self.isFirstFrame = False
            self.encoder.start(output)
            if not self.encoder.wait(self.CAPTURE_TIMEOUT):
                raise PiCameraRuntimeError('Timed out waiting for capture to end')
