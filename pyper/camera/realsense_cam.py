import numpy as np

try:
    import pyrealsense2 as rs
    REALSENSE_AVAILABLE = True
except ImportError:
    print("pyrealsense2 not available. Intel Realsense camera will be disabled")
    REALSENSE_AVAILABLE = False

from pyper.exceptions.exceptions import PyperError
from pyper.video.cv_wrappers.video_capture import VideoCaptureGrabError


class RealSenseException(PyperError):
    pass


class RealSenseCam(object):
    SUPPORTED_FPS = (5, 15, 30, 60, 90)

    def __init__(self, target_fps=None):
        self._verbose = False
        self._pipeline = None
        self.__pipeline_profile = None
        self._config = None
        self.max_fps = RealSenseCam.SUPPORTED_FPS[-1]
        # self.fps = self.max_fps  # FIXME:
        self.fps = 30
        self.actual_fps = None
        # self.default_rgb_frame_shape = (1280, 720)
        self.default_rgb_frame_shape = (848, 480)
        self.default_depth_frame_shape = (848, 480)
        self.initialise_cam(target_fps)

    def __del__(self):
        self.close()

    def set_fps(self, target_fps):
        if target_fps is None:
            target_fps = self.max_fps
        if target_fps not in RealSenseCam.SUPPORTED_FPS:
            # raise RealSenseException("Only the following FPS are supported {}, could not set {}."
            #                          .format(SUPPORTED_FPS, target_fps))
            target_fps = 60
            print("Defaulting to 60 FPS")
        self.fps = target_fps
        return target_fps

    def __enable_streams(self, target_fps=None):
        if target_fps is None:
            target_fps = self.fps
        print('Actual FPS: {}'.format(target_fps))
        # self._config.enable_stream(rs.stream.depth,
        #                            self.default_depth_frame_shape[0], self.default_depth_frame_shape[1],
        #                            rs.format.z16, target_fps)
        self._config.enable_stream(rs.stream.infrared,
                                   self.default_depth_frame_shape[0], self.default_depth_frame_shape[1],
                                   rs.format.y8, target_fps)
        # self._config.enable_stream(rs.stream.color,
        #                            self.default_rgb_frame_shape[0], self.default_rgb_frame_shape[1],
        #                            rs.format.rgb8, target_fps)
        self.actual_fps = target_fps

    def get_shape(self):
        return self.default_rgb_frame_shape

    def __get_rgb_stream(self, device):
        for s in device.sensors:
            if s.get_info(rs.camera_info.name) == 'RGB Camera':
                break
        else:
            raise RealSenseException("No Realsense color cam available")

    def disable_laser(self):
        device = self.__pipeline_profile.get_device()
        for s in device.sensors:
            if s.is_depth_sensor():
                depth_sensor = s
                break
        else:
            raise RealSenseException("No Realsense Depth sensor")

        if depth_sensor.supports(rs.option.laser_power):
            # Query min and max values
            rng = depth_sensor.get_option_range(rs.option.laser_power)
            depth_sensor.set_option(rs.option.laser_power, rng.max)  # Set max power
            depth_sensor.set_option(rs.option.laser_power, 0)   # Disable laser

    def initialise_cam(self, target_fps=None, laser_on=False):
        self.set_fps(target_fps)

        # Configure depth and color streams
        self._pipeline = rs.pipeline()
        self._config = rs.config()

        # Get device product line for setting a supporting resolution
        pipeline_wrapper = rs.pipeline_wrapper(self._pipeline)

        self.__pipeline_profile = self._config.resolve(pipeline_wrapper)
        device = self.__pipeline_profile.get_device()
        self.__get_rgb_stream(device)
        # device_product_line = str(device.get_info(rs.camera_info.product_line))

        if not laser_on:
            self.disable_laser()
        self.__enable_streams()

        # Start streaming
        try:
            self._pipeline.start(self._config)
        except RuntimeError:
            print("Invalid parameters, trying other FPS")
            for i, fps in reversed(list(enumerate(RealSenseCam.SUPPORTED_FPS))):
                try:
                    print("Trying {} FPS".format(fps))
                    self.fps = fps
                    self.__enable_streams()
                    self._pipeline.start(self._config)
                    break
                except RuntimeError as e:
                    if i != 0:
                        continue
                    else:
                        raise e

    def read(self):
        try:
            # frame_set = self._pipeline.poll_for_frames()
            frame_set = self._pipeline.wait_for_frames()
        except RuntimeError as err:
            raise VideoCaptureGrabError(str(err))
        # depth_frame = frame_set.get_depth_frame()
        # if depth_frame:
        #     depth_img = np.asanyarray(depth_frame.get_data())  # TODO: use
        # color_frame = frame_set.get_color_frame()
        # if color_frame:
        #     color_image = np.asanyarray(color_frame.get_data())
        infrared_frame = frame_set.get_infrared_frame()
        if infrared_frame:
            infrared_image = np.asanyarray(infrared_frame.get_data())
            # infrared_image = infrared_image / 65535
            # infrared_image = infrared_image * 255
            infrared_image = np.dstack((infrared_image, infrared_image, infrared_image))

        # if depth_frame and color_frame and infrared_frame:
        # if color_frame and infrared_frame:
        if infrared_frame:
            # TODO: match sizes
            return infrared_image
        else:
            raise VideoCaptureGrabError("No new colour frame available")

    def close(self):
        try:
            self._pipeline.stop()
        except RuntimeError as e:
            if "cannot be called before start" in str(e):
                pass
