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

import platform
from progressbar import *
from time import time

import numpy as np
import cv2

from pyper.contours.object_contour import ObjectContour
from pyper.contours.roi import Circle
from pyper.tracking.tracking_background import Background
from pyper.tracking.tracking_results import TrackingResults
from pyper.utilities import utils
from pyper.utilities.utils import write_structure_not_found_msg, write_structure_size_incorrect_msg
from pyper.video.video_frame import Frame
from pyper.video.video_stream import PiVideoStream, UsbVideoStream, RecordedVideoStream, VideoStreamFrameException
from pyper.cv_wrappers.video_writer import VideoWriter

IS_PI = (platform.machine()).startswith('arm')  # We assume all ARM is a raspberry pi


class Tracker(object):
    """
    A tracker object to track a mouse in a video stream
    """
    def __init__(self, src_file_path=None, dest_file_path=None,
                 threshold=20, min_area=100, max_area=5000,
                 teleportation_threshold=10,
                 bg_start=0, track_from=1, track_to=None,
                 n_background_frames=1, n_sds=5.0,
                 clear_borders=False, normalise=False,
                 plot=False, fast=False, extract_arena=False,
                 infer_location=False,
                 camera_calibration=None, callback=None):
        """
        :param str src_file_path: The source file path to read from (camera if None)
        :param str dest_file_path: The destination file path to save the video
        :param int threshold: The numeric threshold for the masks (0<t<256)
        :param int min_area: The minimum area in pixels to be considered a valid mouse
        :param teleportation_threshold: The maximum number of pixels the mouse can \
        move in either dimension (x,y) between 2 frames.
        :param int bg_start: The frame to use as first background frame
        :param int n_background_frames: The number of frames to use for the background\
        A number >1 means average
        :param int n_sds: The number of standard deviations the signal has to be above\
        to be considered above threshold. This option is not used if \
        nBackgroundFrames < 2
        :param int track_from: The frame to start tracking from
        :param int track_to: The frame to stop tracking at
        :param bool clear_borders: Whether to clear objects that touch the outer borders\
        of the image.
        :param bool normalise: TODO
        :param bool plot: Whether to display the data during tracking:
        :param bool fast: Whether to skip some processing (e.g. frame denoising) for \
        the sake of acquisition speed.
        :param bool extract_arena: Whether to detect the arena (it should be brighter than\
        the surrounding) from the background as an ROI.
        :param callback: The function to be executed upon finding the mouse in the ROI \
        during tracking.
        :type callback: `function`
        """

        if callback is not None: self.handle_object_in_tracking_roi = callback
        track_range_params = (bg_start, n_background_frames)
        self.raw_out_stream = None
        if src_file_path is None:
            if IS_PI:
                self._stream = PiVideoStream(dest_file_path, *track_range_params)
            else:
                self._stream = UsbVideoStream(dest_file_path, *track_range_params)  # FIXME: fix fps
                base_path, ext = os.path.splitext(dest_file_path)
                raw_out_path = "{}_raw{}".format(base_path, ext)
                self.raw_out_stream = VideoWriter(raw_out_path,
                                                  self._stream.video_writer.codec,
                                                  self._stream.video_writer.fps,
                                                  self._stream.video_writer.frame_shape,
                                                  is_color=True)  # FIXME: make optional
        else:
            self._stream = RecordedVideoStream(src_file_path, *track_range_params)
        
        self.threshold = threshold
        self.min_area = min_area
        self.max_area = max_area
        self.teleportation_threshold = teleportation_threshold
        
        self.track_from = track_from
        self.track_to = track_to
        
        self.clear_borders = clear_borders
        self.normalise = normalise
        self.plot = plot
        self.fast = fast
        self.extract_arena = extract_arena
        self.infer_location = infer_location

        self.bg = Background(n_sds)
        
        self.camera_calibration = camera_calibration

        self.results = TrackingResults()

        self.current_frame_idx = 0
        self.current_frame = None  # Give shape np.empty_like()
        self.silhouette = None  # np.empty_like()

        self.arena = None
        self.roi = None
        self.tracking_region_roi = None
        self.measure_roi = None

    def set_roi(self, roi):
        """Set the region of interest and enable it"""
        self.roi = roi
        if roi is not None:
            self._make_bottom_square()

    def set_tracking_region_roi(self, roi):
        self.tracking_region_roi = roi

    def set_measure_roi(self, roi):
        self.measure_roi = roi
        
    def _extract_arena(self):
        """
        Finds the arena in the current background frame and
        converts it to an roi object.
        
        :return: arena
        :rtype: Circle
        """
        if self.extract_arena:
            mask = self.bg.to_mask(self.threshold)
            cnt = self._get_biggest_contour(mask)
            arena = Circle(*cv2.minEnclosingCircle(cnt))
            self.arena = arena
        
    def _make_bottom_square(self):  # TODO: extract
        """
        Creates a set of diagonally opposed points to use as the corners
        of the square displayed by the default callback method.
        """
        bottom_right_pt = self._stream.size
        top_left_pt = tuple([p-50 for p in bottom_right_pt])
        self.bottom_square = (top_left_pt, bottom_right_pt)

    def _create_pbar(self):
        widgets = ['Tracking frames: ', Percentage(), Bar()]
        pbar = ProgressBar(widgets=widgets, maxval=self._stream.n_frames).start()
        return pbar

    def _set_default_results(self):
        if self.infer_location:
            self.results.repeat_last()
        else:
            self.results.append_defaults()

    def is_before_frame(self, fid):
        return fid < self._stream.bg_start_frame

    def is_after_frame(self, fid):
        return self.track_to and (fid > self.track_to)
        
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
        self.set_roi(roi)
        
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
                return self.results.positions

    def update_img(self, dest_img, src_img):
        if dest_img is None or dest_img.ndim != src_img.ndim:
            dest_img = src_img.copy()
        if src_img.ndim == 2:
            dest_img[:] = src_img
        elif src_img.ndim == 3:
            dest_img[::] = src_img
        else:
            raise NotImplementedError("Images must be 1 or 2 color 2D images")
        return dest_img

    def track_frame(self, pbar=None, record=False, requested_output='raw'):  # TODO: improve calls to "if record: self._stream.save(frame)"
        try:
            frame = self._stream.read()
            self.current_frame = self.update_img(self.current_frame, frame)
            self._set_default_results()
            if self.camera_calibration is not None:
                frame = Frame(self.camera_calibration.remap(frame))
            fid = self._stream.current_frame_idx
            if self.is_after_frame(fid):
                raise EOFError("End of tracking reached")

            result_frame = frame  # image_provider colorises and copies
            if self.raw_out_stream is not None:
                self.raw_out_stream.save_frame(frame)
            if self.is_before_frame(fid):
                pass
            elif self._stream.is_bg_frame():
                self.bg.build(frame)
                self.arena = self._extract_arena()
                if record: self._stream.save(frame)
            elif self._stream.bg_end_frame < fid < self.track_from:
                if record: self._stream.save(frame)
            else:  # Tracked frame
                if fid == self.track_from: self.bg.finalise()
                contour_found, sil = self._track_frame(frame, 'b', requested_output=requested_output)
                self.after_frame_track()
                self.silhouette = self.update_img(self.silhouette, sil)
                if not contour_found:
                    if record: self._stream.save(frame)
                    write_structure_not_found_msg(self.silhouette, self.silhouette.shape[:2], self.current_frame_idx)
                else:
                    self._check_mouse_in_roi()
                    self._plot()
                    if record: self._stream.save(self.silhouette)
                result_frame = self.silhouette
            if pbar is not None: pbar.update(self._stream.current_frame_idx)
            return result_frame, self.results.get_last_position(), self.results.get_last_dist_from_arena_pair()
        except VideoStreamFrameException as e:
            print('Error with video_stream at frame {}: \n{}'.format(fid, e))
        except (KeyboardInterrupt, EOFError) as e:
            if pbar is not None: pbar.finish()
            msg = "Recording stopped by user" if (type(e) == KeyboardInterrupt) else str(e)
            self._stream.stop_recording(msg)
            raise EOFError

    def after_frame_track(self):
        pass

    def _track_frame(self, frame, requested_color='r', requested_output='raw'):
        """
        Get the position of the mouse in frame and append to self.results
        Returns the mask of the current frame with the mouse potentially drawn

        :param frame: The video frame to use.
        :type: video_frame.Frame
        :param str requested_color: A character (for list of supported characters see ObjectContour)\
         indicating the color to draw the contour
        :param str requested_output: Which frame type to output (one of ['raw', 'mask', 'diff'])
        :returns: silhouette
        :rtype: binary mask or None
        """
        processed_frame = self._pre_process_frame(frame)
        silhouette, diff = self._get_silhouette(processed_frame)
        biggest_contour = self._get_biggest_contour(silhouette)

        if IS_PI and self.fast:
            requested_output = 'mask'
        plot_silhouette, color_is_default = self._get_plot_silhouette(requested_output, frame, diff, silhouette)
        color = 'w' if color_is_default else requested_color

        contour_found = False
        if biggest_contour is not None:
            area = cv2.contourArea(biggest_contour)
            mouse = ObjectContour(biggest_contour, plot_silhouette, contour_type='raw', color=color)
            if self.plot:
                mouse.draw()  # even if wrong size to held spot issues
                self._draw_subregion_roi(plot_silhouette)
            if self.min_area < area < self.max_area:
                distances = (self._get_distance_from_arena_center(), self._get_distance_from_arena_border())
                self.results.update(mouse.centre, area, self.measure_callback(frame), distances)
                self._check_teleportation(frame, silhouette)
                contour_found = True
            else:
                if self.plot:
                    self._handle_bad_size_contour(area, plot_silhouette)
                else:
                    self._handle_bad_size_contour(area)
        else:
            self._fast_print('Frame {}, no contour found'.format(self._stream.current_frame_idx))
        return contour_found, plot_silhouette

    def _check_mouse_in_roi(self):
        """
        Checks whether the mouse is within the specified ROI and
        calls the specified callback method if so.
        """
        if self.roi is not None:
            if self.results.last_pos_is_default():
                return
            if self.roi.contains_point(self.results.get_last_position()):
                self.handle_object_in_tracking_roi()
                self.silhouette = self.silhouette.copy()  # OPTIMISE:
            
    def _get_distance_from_arena_border(self):  # FIXME: merge and move
        if self.results.last_pos_is_default():
            return
        if self.extract_arena:
            last_pos = self.results.get_last_position()
            return self.arena.dist_from_border(last_pos)
            
    def _get_distance_from_arena_center(self):  # FIXME: merge and move
        if self.results.last_pos_is_default():
            return
        if self.extract_arena:
            last_pos = self.results.get_last_position()
            return self.arena.dist_from_centre(last_pos)
            
    def paint(self, frame, roi_color='y', arena_color='m'):
        if self.roi is not None:
            roi_contour = ObjectContour(self.roi.points, frame, contour_type='raw',
                                        color=roi_color, line_thickness=2)
            roi_contour.draw()
        if self.extract_arena:
            arena_contour = ObjectContour(self.arena.points, frame, contour_type='raw',
                                          color=arena_color, line_thickness=2)
            arena_contour.draw()

    def _plot(self):
        """
        Displays the current frame with the mouse trajectory and potentially the ROI and the
        Arena ROI if these have been specified.
        """
        if self.plot:
            sil = self.silhouette
            self.paint(sil)
            sil.display(win_name='Diff', text='Frame: {}'.format(self._stream.current_frame_idx),
                        curve=self.results.positions)

    def handle_object_in_tracking_roi(self):
        """
        The method called when the mouse is found in the roi.
        This method is meant to be overwritten in subclasses of Tracker.
        """
        self.results.overwrite_last_in_tracking_roi(True)
        cv2.rectangle(self.silhouette, self.bottom_square[0], self.bottom_square[1], (0, 255, 255), -1)

    def measure_callback(self, frame):
        if self.measure_roi is not None:
            mask = self.measure_roi.to_mask(frame)
            values = np.extract(mask, frame)
            return values.mean()
        else:
            return float('NaN')
    
    def _pre_process_frame(self, frame):
        treated_frame = frame.gray(self.fast)   # TODO: check if we should separate setting
        if not self.fast:
            treated_frame = treated_frame.denoise().blur()
        return treated_frame

    def _get_plot_silhouette(self, requested_output, frame, diff, silhouette):  # OPTIMISE:
        color_is_default = False
        if self.plot:
            if requested_output == 'raw':
                plot_silhouette = frame.color(in_place=True)
            elif requested_output == 'mask':
                plot_silhouette = silhouette
                color_is_default = True
            elif requested_output == 'diff':
                plot_silhouette = diff.color(in_place=True)
            else:
                raise NotImplementedError("Expected one of ('raw', 'mask', 'diff') "
                                          "for requested_output, got: {}".format(requested_output))
        else:
            color_is_default = True
            plot_silhouette = frame
        return plot_silhouette, color_is_default

    def _handle_bad_size_contour(self, area, img=None):
        if area > self.max_area:
            msg = 'Biggest structure too big ({} > {})'.format(area, self.max_area)
        else:
            msg = 'Biggest structure too small ({} < {})'.format(area, self.min_area)
        self._fast_print(msg)
        if img is not None:
            write_structure_size_incorrect_msg(img, img.shape[:2], msg)

    def _draw_subregion_roi(self, img, color='y'):
        if self.tracking_region_roi is not None:
            test_roi = ObjectContour(self.tracking_region_roi.points, img, contour_type='raw', color=color)
            test_roi.draw()

    def _fast_print(self, in_str):
        """
        Print only if not `fast` option not selected

        :param str in_str: The string to print
        :return:
        """
        if not self.fast:
            print(in_str)
        
    def _check_teleportation(self, frame, silhouette):
        """
        Check if the mouse moved too much, which would indicate an issue with the tracking
        notably the fitting in the past. If so, call self._stream.stopRecording() and raise
        EOFError.
        
        :param frame: The current frame (to be saved for troubleshooting if teleportation occurred)
        :type frame: video_frame.Frame
        :param silhouette: The binary mask of the current frame\
         (to be saved for troubleshooting if teleportation occurred)
        :type silhouette: video_frame.Frame
        
        :raises: EOFError if the mouse teleported
        """
        if not self.results.has_non_default_position():  # No tracking yet
            return
        last_vector = self.results.get_last_movement_vector()
        if (last_vector > self.teleportation_threshold).any():
            # if self.infer_location:
            #     self.positions[-1] = self.positions[-2]
            # else:
            silhouette.save('teleporting_silhouette.tif')  # Used for debugging
            frame.save('teleporting_frame.tif')
            err_msg = 'Frame: {}, mouse teleported from {} to {}\n'\
                .format(self._stream.current_frame_idx, *self.results.get_last_pos_pair())
            err_msg += 'Please see teleporting_silhouette.tif and teleporting_frame.tif for debugging'
            self._stream.stop_recording(err_msg)
            raise EOFError('Teleportation')

    def _get_biggest_contour(self, silhouette):
        """
        We need to rerun if too many contours are found as it should means
        that the findContours function returned nonsense.
        
        :param silhouette: The binary mask in which to find the contours
        :type silhouette: video_frame.Frame
        
        :return: The contours and the biggest contour from the mask (None, None) if no contour found
        """
        contours, hierarchy = cv2.findContours(np.copy(silhouette),
                                               mode=cv2.RETR_LIST,
                                               method=cv2.CHAIN_APPROX_NONE)  # TODO: is CHAIN_APPROX_SIMPLE better?
        if contours:
            descending_contours = sorted(contours, key=cv2.contourArea, reverse=True)
            if self.tracking_region_roi is None:
                return descending_contours[0]
            else:
                for cnt in descending_contours:  # use cv2.contourArea(c)
                    closed_contour = len(cnt) >= 4
                    if closed_contour and self.tracking_region_roi.contains_contour(cnt):
                        return cnt
                    else:
                        continue
                return None  # all contours have failed
        
    def _get_silhouette(self, frame):
        """
        Get the binary mask (8bits) of the mouse 
        from the thresholded difference between frame and the background
        
        :param frame: The current frame to analyse
        :type frame: video_frame.Frame
        
        :returns: silhouette (the binary mask)
        :rtype: video_frame.Frame
        """
        if self.normalise:
            frame = frame.normalise(self.bg.global_avg)
        diff = self.bg.diff(frame)
        if self.bg.use_sd:
            threshold = self.bg.get_std_threshold()
            silhouette = diff > threshold
            silhouette = silhouette.astype(np.uint8) * 255
        else:
            diff = diff.astype(np.uint8)  # OPTIMISE
            silhouette = diff.threshold(self.threshold)
        if self.clear_borders:
            silhouette.clear_borders()
        return silhouette, diff

