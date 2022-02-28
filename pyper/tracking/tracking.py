# -*- coding: utf-8 -*-
"""
*******************
The tracking module
*******************

IT is the main module after the interface.
This module used inspiration from code developed by Antonio Gonzalez for the trackFrame function

If running on an ARM processor, it assumes the platform is a Raspberry Pi and thus uses the pi camera
instead of a usb camera by default. It also slightly optimises for speed.
:author: crousse
"""
from __future__ import division

import os
from time import time

import numpy as np

from pyper.contours import object_contour
from tqdm import tqdm

from pyper.contours.contours_manager import ContoursManager
from pyper.exceptions.exceptions import VideoStreamTypeException
from pyper.tracking.structure_tracker import StructureTracker  # WARNING: Required for dynamic loading of classes
from pyper.tracking.tracking_background import Background
from pyper.utilities.utils import split_file_name_digits
from pyper.video.video_frame import Frame, update_img
from pyper.video.video_stream import PiVideoStream, UsbVideoStream, RecordedVideoStream, VideoStreamFrameException, \
    IS_PI, RealSenseRgbVideoStream, KinectV2RgbVideoStream
from pyper.video.cv_wrappers.video_writer import VideoWriter
from pyper.utilities import utils


class Tracker(object):
    """
    A tracker object to track a specimen in a video stream
    """

    def __init__(self, params, src_file_path=None, dest_file_path=None,
                 camera_calibration=None, requested_fps=None):
        """
        :param GuiParameters params: The various configuration parameters to run the segmentation
        :param str src_file_path: The source file path to read from (camera if None)
        :param str dest_file_path: The destination file path to save the video
        :param camera_calibration.CameraCalibration camera_calibration: The object providing the calibration of the lens
        to compensate for barrel distortion
        """
        self.params = params
        self.arena = None

        track_range_params = (self.params.bg_frame_idx,
                              self.params.n_background_frames)  # FIXME: should be whole for e.g. transcode
        self.raw_out_stream = None
        if src_file_path is None:  # i.e. we record
            if IS_PI:
                self._stream = PiVideoStream(dest_file_path, *track_range_params, requested_fps=requested_fps)
            else:
                cam_name = self.params.cam_name.lower()
                if cam_name.startswith("usb"):
                    self._stream = UsbVideoStream(dest_file_path, *track_range_params, requested_fps=requested_fps,
                                                  cam_nb=int(self.params.cam_name[-1]))
                elif cam_name == "kinect":
                    self._stream = KinectV2RgbVideoStream(dest_file_path, *track_range_params,
                                                          requested_fps=requested_fps)
                elif cam_name == "realsense":
                    self._stream = RealSenseRgbVideoStream(dest_file_path, *track_range_params,
                                                           requested_fps=requested_fps)
                else:
                    raise VideoStreamTypeException('"{}" is not a valid camera type. Supported types are {}'
                                                   .format(cam_name, ("usbX", "kinect", "realsense")))
                base_name, ext, idx, n_digits = split_file_name_digits(dest_file_path)
                if idx is not None:
                    raw_out_path = '{}raw_{}{}'.format(base_name, str(idx).zfill(n_digits), ext)
                    raw_out_path = os.path.join(os.path.dirname(dest_file_path), raw_out_path)
                else:
                    base_path, ext = os.path.splitext(dest_file_path)
                    raw_out_path = "{}_raw{}".format(base_path, ext)
                self.raw_out_stream = VideoWriter(raw_out_path,
                                                  self._stream.video_writer.codec,
                                                  self._stream.video_writer.fps,
                                                  self._stream.video_writer.frame_shape,
                                                  is_color=True)  # TODO: make optional
        else:
            self._stream = RecordedVideoStream(src_file_path, *track_range_params)

        self.bg = Background(self.params.n_sds)

        self.camera_calibration = camera_calibration

        self.current_frame_idx = 0
        self.current_frame = None  # Give shape np.empty_like()

        self.structures = []
        for struct_name, struct_params in self.params.structures.items():
            if struct_params.is_enabled:
                struct_class = struct_params.tracker_class
                self.structures.append(struct_class(struct_name, self.params, struct_params, arena=self.arena,
                                                    stream=self._stream, raw_stream=self.raw_out_stream,
                                                    background=self.bg))

    def reset_measures(self):
        for struct in self.structures:
            struct.reset()

    def save_results(self):
        for struct in self.structures:
            struct.multi_results.save(struct_name=struct.name)

    def close_all(self):
        for struct in self.structures:
            struct.close_all()

    def open_all(self):
        for struct in self.structures:
            struct.open_all()

    def set_start_time(self, start_time):
        for struct in self.structures:
            struct.multi_results.set_start_time(start_time)

    def set_roi(self, roi, idx):
        """Set the region of interest and enable it"""
        if roi is not None:
            self.structures[idx].roi = roi
            self.structures[idx].bottom_square = self.get_bottom_square()

    def set_tracking_region_roi(self, roi, idx):
        self.structures[idx].tracking_region_roi = roi

    def set_measure_roi(self, roi, idx):
        self.structures[idx].measure_roi = roi

    def _extract_arena(self, shape='circle'):
        """
        Finds the arena in the current background frame and
        converts it to an roi object.

        :return: arena
        :rtype: Roi
        """
        if self.params.extract_arena:
            mask = self.bg.to_mask(self.params.detection_threshold)
            cnt_manager = ContoursManager.from_mask(mask)
            self.arena = contour_to_roi(cnt_manager.get_biggest(), shape)

    def get_bottom_square(self, square_width=50):
        """
        Creates a set of diagonally opposed points to use as the corners
        of the square displayed by the default callback method.
        """
        bottom_right_pt = self._stream.size
        top_left_pt = tuple([p - square_width for p in bottom_right_pt])
        cnt = object_contour.diagonal_to_rectangle_points(top_left_pt, bottom_right_pt)
        bottom_square = object_contour.ObjectContour(cnt, None, 'rectangle', 'c', -1)
        return bottom_square

    def _create_pbar(self):
        pbar = tqdm(desc='Tracking frames: ', total=self._stream.n_frames)
        return pbar

    def __is_before_frame(self, fid):
        return fid < self._stream.bg_start_frame

    def __is_after_frame(self, fid):
        return self.params.end_frame_idx >= 0 and (fid > self.params.end_frame_idx)

    def track(self, roi=None, record=False, check_fps=False, reset=True):
        """The main function. Loops until the end of the recording (ctrl+c if acquiring).

        :param roi: optional roi e.g. Circle((250, 350), 25)
        :type roi: roi sub-class
        :param bool check_fps: Whether to print the current frame per second processing speed
        :param bool record: Whether to save the frames being processed
        :param bool reset: whether to reset the recording (restart the background and arena ...).\
        If this parameter is False, the recording will continue from the previous frame.

        :returns list positions:
        """
        if len(self.structures) == 1:
            self.set_roi(roi, 0)
        else:
            raise NotImplementedError('Multiple structures not supported yet for this function')

        is_recording = type(self._stream) == RecordedVideoStream
        self.bg.clear()
        if is_recording:
            pbar = self._create_pbar()
        elif IS_PI:
            self._stream.restart_recording(reset)
            pbar = None
        if check_fps: prev_time = time()
        while True:
            try:
                if check_fps: prev_time = utils.check_fps(prev_time)
                self.current_frame_idx = self._stream.current_frame_idx + 1
                self.track_frame(pbar=pbar, record=record)  # TODO: requested_color='r'
            except EOFError:
                return [struct.multi_results.positions for struct in self.structures]

    def track_frame(self, pbar=None, record=False,
                    requested_output='raw'):  # TODO: improve calls to "if record: self._stream.save(frame)"
        fid = None  # if undefined before exception
        try:
            frame = self._stream.read()
            sil = frame  # Default to frame if untracked
            self.current_frame = update_img(self.current_frame, frame)
            for struct in self.structures:
                struct.set_default_results()
            if self.camera_calibration is not None:
                frame = Frame(self.camera_calibration.remap(frame))
            fid = self._stream.current_frame_idx
            if self.__is_after_frame(fid):
                raise EOFError("End of tracking reached")

            if self.raw_out_stream is not None:
                self.raw_out_stream.save_frame(frame)
            if self.__is_before_frame(fid):
                pass
            elif self._stream.is_bg_frame():
                self.bg.build(frame)  # FIXME: color=True if (f(structure) ==> !+ bg
                self.arena = self._extract_arena()
                if record: self._stream.save(frame)
            elif self._stream.bg_end_frame < fid < self.params.start_frame_idx:
                if record: self._stream.save(frame)
            else:  # Tracked frame
                if fid == self.params.start_frame_idx: self.bg.finalise()  # FIXME: does not seem to work for bg with source
                for struct_idx, struct in enumerate(self.structures):
                    contour_found, _sil = struct.track_frame(frame, 'b', requested_output=requested_output)
                    if struct_idx == 0:  # TO superimpose tracking. TODO: find better solution
                        sil = _sil
                    else:
                        if requested_output == "mask":  # fuse the masks
                            print(sil.shape, sil.dtype, _sil.shape, _sil.dtype)
                            sil = np.logical_or(sil, _sil)
                            sil = Frame(sil.astype(_sil.dtype) * 255)
                    struct.mask = update_img(struct.mask, sil)
                    if not contour_found:
                        if record: self._stream.save(frame)
                        utils.write_structure_not_found_msg(sil, sil.shape[:2], self.current_frame_idx)
                    else:
                        struct.check_specimen_in_roi(sil)
                        struct.paint_frame(sil, self.should_update_vid)
                        if record: self._stream.save(struct.mask)  # FIXME: needs n_structures streams. No use raw and append to frame
                self.after_frame_track()
            if pbar is not None: pbar.update(self._stream.current_frame_idx)
            return sil  # FIXME: needs to superimpose both trackings
        except VideoStreamFrameException as e:
            print('Error with video_stream at frame {}: \n{}'.format(fid, e))
        except (KeyboardInterrupt, EOFError) as e:
            if pbar is not None: pbar.close()
            msg = "Recording stopped by user" if (type(e) == KeyboardInterrupt) else str(e)
            self._stream.stop_recording(msg)
            raise EOFError

    @property
    def should_update_vid(self):
        return (self._stream.current_frame_idx % self.params.curve_update_period) == 0  # TODO: improve

    def after_frame_track(self):
        """
        To be implemented in derived class to perform action after each frame track

        :return:
        """
        pass
