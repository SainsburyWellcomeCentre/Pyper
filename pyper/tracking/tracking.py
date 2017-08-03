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

import numpy as np
import cv2
from progressbar import *

from time import time

from pyper.contours.object_contour import ObjectContour
from pyper.video.video_frame import Frame
from pyper.video.video_stream import PiVideoStream, UsbVideoStream, RecordedVideoStream, VideoStreamFrameException
from pyper.contours.roi import Circle

IS_PI = (platform.machine()).startswith('arm')  # We assume all ARM is a raspberry pi


class Viewer(object):
    """
    A viewer class, a form of simplified Tracker for display purposes
    It can be used to retrieve some parameters of the video or just display
    """
    def __init__(self, src_file_path=None, bg_start=0, n_background_frames=1, delay=5):
        """
        :param str src_file_path: The source file path to read from (camera if None)
        :param int bg_start: The frame to use as first background frame
        :param int n_background_frames: The number of frames to use for the background\
        A number >1 means average
        :param int delay: The time in ms to wait between frames
        """
        track_range_params = (bg_start, n_background_frames)
        if src_file_path is None:
            if IS_PI:
                self._stream = PiVideoStream(dest_file_path, *track_range_params)
            else:
                self._stream = UsbVideoStream(dest_file_path, *track_range_params)
        else:
            self._stream = RecordedVideoStream(src_file_path, *track_range_params)
        self.delay = delay
        
    def view(self):
        """
        Displays the recording to the user and allows assignment of background frames, tracking start and end
        The user can stop by pressing 'q'
        
        :return int bg_frame: set using the 'b' key
        :return int track_start: set using the 's' key
        :return int track_end:set using the 'q' key
        """
        is_recording = hasattr(self._stream, 'n_frames')
        if is_recording:
            widgets = ['Video Progress: ', Percentage(), Bar()]
            pbar = ProgressBar(widgets=widgets, maxval=self._stream.n_frames).start()
        bg_frame = track_start = track_end = None
        while True:
            try:
                frame = self._stream.read()
                frame_id = self._stream.current_frame_idx
                if frame.shape[2] == 1:
                    frame = np.dstack([frame]*3)
                if not frame.dtype == np.uint8:
                    frame = frame.astype(np.uint8)
                frame = frame.copy()
                kbd_code = frame.display(win_name='Frame',
                                         text='Frame: {}'.format(frame_id),
                                         delay=self.delay,
                                         get_code=True)
                kbd_code = kbd_code if kbd_code == -1 else chr(kbd_code & 255)
                if kbd_code == 'b': bg_frame = frame_id
                elif kbd_code == 's': track_start = frame_id
                elif kbd_code == 'e': track_end = frame_id
                elif kbd_code == 'q':
                    break
                    
                if (bg_frame is not None) and (track_start is not None) and (track_end is not None):
                    break
                if is_recording: pbar.update(frame_id)
            except VideoStreamFrameException: pass
            except (KeyboardInterrupt, EOFError) as e:
                if is_recording: pbar.finish()
                msg = "Recording stopped by user" if (type(e) == KeyboardInterrupt) else str(e)
                self._stream.stop_recording(msg)
                break
        if track_end is None:
            track_end = self._stream.current_frame_idx
        if bg_frame is None:
            bg_frame = 0
        if __debug__:
            print(bg_frame, track_start, track_end)
        return bg_frame, track_start, track_end
        
    def time_str_to_frame_idx(self, time_str):
        """
        Returns the frame number that corresponds to that time.
        
        :param str time_str: A string of the form 'mm:ss'
        :return Idx: The corresponding frame index
        :rtype: int
        """
        return self._stream.time_str_to_frame_idx(time_str)


def write_structure_not_found_msg(img, img_size, frame_idx):
    """
    Write an error message on the image supplied as argument. The operation is performed in place

    :param int frame_idx: The frame at which the structure cannot be found
    :param img: The source image to write onto
    :param tuple img_size: The size of the source image
    """
    line1 = "No contour found at frame: {}".format(frame_idx)
    line2 = "Please check your parameters"
    line3 = "And ensure specimen is there"
    x = int(50)
    y = int(img_size[0] / 2)
    y_spacing = 40
    font_color = (255, 255, 0)  # yellow
    font_size = 0.75  # percent
    font_type = int(2)
    cv2.putText(img, line1, (x, y), font_type, font_size, font_color)
    y += y_spacing
    cv2.putText(img, line2, (x, y), font_type, font_size, font_color)
    y += y_spacing
    cv2.putText(img, line3, (x, y), font_type, font_size, font_color)


def write_structure_size_incorrect_msg(img, img_size, msg):
    x = int(50)
    y_spacing = 40
    y = int(img_size[0] / 2) - y_spacing
    font_color = (255, 255, 0)  # yellow
    font_size = 0.75  # percent
    font_type = int(2)
    cv2.putText(img, msg, (x, y), font_type, font_size, font_color)


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

        if callback is not None: self.callback = callback
        track_range_params = (bg_start, n_background_frames)
        if src_file_path is None:
            if IS_PI:
                self._stream = PiVideoStream(dest_file_path, *track_range_params)
            else:
                self._stream = UsbVideoStream(dest_file_path, *track_range_params)
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
        
        self.n_sds = n_sds
        self.bg = None
        self.bg_std = None
        
        self.camera_calibration = camera_calibration
        
        self.default_pos = (-1, -1)
        self.positions = []
        self.tracking_region_roi = None
        
    def _extract_arena(self):
        """
        Finds the arena in the current background frame and
        converts it to an roi object.
        
        :return: arena
        :rtype: Circle
        """
        bg = self.bg.copy()
        bg = bg.astype(np.uint8)
        mask = bg.threshold(self.threshold)
        cnt = self._get_biggest_contour(mask)
        arena = Circle(*cv2.minEnclosingCircle(cnt))
        self.distances_from_arena = []
        return arena
        
    def _make_bottom_square(self):
        """
        Creates a set of diagonaly opposed points to use as the corners
        of the square displayed by the default callback method.
        """
        bottom_right_pt = self._stream.size
        top_left_pt = tuple([p-50 for p in bottom_right_pt])
        self.bottom_square = (top_left_pt, bottom_right_pt)
        
    def track(self, roi=None, check_fps=False, record=False, reset=True):
        """The main function. Loops until the end of the recording (ctrl+c if acquiring).
        
        :param roi: optional roi e.g. Circle((250, 350), 25)
        :type roi: roi sub-class
        :param bool check_fps: Whether to print the current frame per second processing speed
        :param bool record: Whether to save the frames being processed
        :param bool reset: whether to reset the recording (restart the background and arena ...).\
        If this parameter is False, the recording will continue from the previous frame.
        
        :returns list positions:
        """
        self.roi = roi
        if roi is not None:
            self._make_bottom_square()
        
        is_recording = type(self._stream) == RecordedVideoStream
        self.bg = None  # reset for each track
        if is_recording:
            widgets = ['Tracking frames: ', Percentage(), Bar()]
            pbar = ProgressBar(widgets=widgets, maxval=self._stream.n_frames).start()
        elif IS_PI:
            self._stream.restart_recording(reset)

        if check_fps: prev_time = time.time()
        while True:
            try:
                if check_fps: prev_time = self._check_fps(prev_time)
                frame = self._stream.read()
                if self.camera_calibration is not None:
                    frame = self.camera_calibration.remap(frame)
                fid = self._stream.current_frame_idx
                if self.track_to and (fid > self.track_to):
                    raise KeyboardInterrupt  # stop recording
                    
                if fid < self._stream.bg_start_frame:
                    continue  # Skip junk frames
                elif self._stream.is_bg_frame():
                    self._build_bg(frame)
                elif self._stream.bg_end_frame < fid < self.track_from:
                    continue  # Skip junk frames
                else:  # Tracked frame
                    if fid == self.track_from: self._finalise_bg()
                    contour_found, sil = self._track_frame(frame)
                    self.silhouette = sil.copy()
                    if not contour_found:
                        continue
                    if self.roi is not None: self._check_mouse_in_roi()
                    if self.plot: self._plot()
                    if record: self._stream._save(self.silhouette)
                if is_recording: pbar.update(self._stream.current_frame_idx)
            except VideoStreamFrameException as e:
                print('Error with video_stream at frame {}: \n{}'.format(fid, e))
            except (KeyboardInterrupt, EOFError) as e:
                if is_recording: pbar.finish()
                msg = "Recording stopped by user" if (type(e) == KeyboardInterrupt) else str(e)
                self._stream.stop_recording(msg)
                return self.positions
                
    def _last_pos_is_default(self):
        last_pos = tuple(self.positions[-1])
        if last_pos == self.default_pos:
            return True
        else:
            return False

    def _check_mouse_in_roi(self):
        """
        Checks whether the mouse is within the specified ROI and
        calls the specified callback method if so.
        """
        if self._last_pos_is_default():
            return
        if self.roi.point_in_roi(self.positions[-1]):
            self.callback()
            self.silhouette = self.silhouette.copy()
            
    def _get_distance_from_arena_border(self):
        if self._last_pos_is_default():
            return
        if self.extract_arena:
            last_pos = tuple(self.positions[-1])
            return self.arena.dist_from_border(last_pos)
            
    def _get_distance_from_arena_center(self):
        if self._last_pos_is_default():
            return
        if self.extract_arena:
            last_pos = tuple(self.positions[-1])
            return self.arena.dist_from_center(last_pos)
            
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
        sil = self.silhouette
        self.paint(sil)
        sil.display(win_name='Diff', text='Frame: {}'.format(self._stream.current_frame_idx), curve=self.positions)

    def callback(self):
        """
        The method called when the mouse is found in the roi.
        This method is meant to be overwritten in subclasses of Tracker.
        """
        cv2.rectangle(self.silhouette, self.bottom_square[0], self.bottom_square[1], (0, 255, 255), -1)

    def _build_bg(self, frame):
        """
        Initialise the background if empty, expand otherwise.
        Will also initialise the arena roi if the option is selected
        
        :param frame: The video frame to use as background or part of the background.
        :type frame: video_frame.Frame
        """
        if __debug__:
            print("Building background")
        bg = frame.denoise().blur().gray()
        if self.bg is None:
            self.bg = bg
        else:
            self.bg = Frame(np.dstack((self.bg, bg)))
        if self.extract_arena:
            self.arena = self._extract_arena()
                
    def _finalise_bg(self):
        """
        Finalise the background (average stack and compute SD if more than one image)
        """
        if self.bg.ndim > 2:
            self.bg_std = np.std(self.bg, axis=2)
            self.bg = np.average(self.bg, axis=2)
        if self.normalise:
            self.bg_avg_avg = self.bg.mean()  # TODO: rename
    
    def _track_frame(self, frame, requested_color='r', requested_output='raw'):
        """
        Get the position of the mouse in frame and append to self.positions
        Returns the mask of the current frame with the mouse potentially drawn
        
        :param frame: The video frame to use.
        :type: video_frame.Frame
        :param str requested_color: A character (for list of supported characters see ObjectContour)\
         indicating the color to draw the contour
        :param str requested_output: Which frame type to output (one of ['raw', 'mask', 'diff'])
        :returns: silhouette
        :rtype: binary mask or None
        """
        treated_frame = frame.gray()
        if not IS_PI and not self.fast:
            treated_frame = treated_frame.denoise().blur()
        silhouette, diff = self._get_silhouette(treated_frame)
        
        biggest_contour = self._get_biggest_contour(silhouette)

        if IS_PI and self.fast:
            requested_output = 'mask'
        self.positions.append(self.default_pos)
        if self.plot:
            if requested_output == 'raw':
                plot_silhouette = (frame.color()).copy()
                color = requested_color
            elif requested_output == 'mask':
                plot_silhouette = silhouette.copy()
                color = 'w'
            elif requested_output == 'diff':
                plot_silhouette = (diff.color()).copy()
                color = requested_color
            else:
                raise NotImplementedError("Expected one of ('raw', 'mask', 'diff') "
                                          "for requested_output, got: {}".format(requested_output))
        else:
            color = 'w'
            plot_silhouette = frame
        contour_found = False
        if biggest_contour is not None:
            area = cv2.contourArea(biggest_contour)
            mouse = ObjectContour(biggest_contour, plot_silhouette, contour_type='raw', color=color)
            if self.plot:
                mouse.draw()  # even if wrong size to held spot issues
                self._draw_subregion_roi(plot_silhouette)
            if self.min_area < area < self.max_area:
                self.positions[-1] = mouse.centre
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

    def _draw_subregion_roi(self, img, color='y'):
        if self.tracking_region_roi is not None:
            test_roi = ObjectContour(self.tracking_region_roi.points, img, contour_type='raw', color=color)
            test_roi.draw()

    def _handle_bad_size_contour(self, area, img=None):
        if area > self.max_area:
            msg = 'Biggest structure too big ({} > {})'.format(area, self.max_area)
        else:
            msg = 'Biggest structure too small ({} < {})'.format(area, self.min_area)
        self._fast_print(msg)
        if img is not None:
            write_structure_size_incorrect_msg(img, img.shape[:2], msg)

    def _fast_print(self, in_str):
        """
        Print only if not `fast` option not selected

        :param str in_str: The string to print
        :return:
        """
        if not self.fast:
            print(in_str)

    @staticmethod
    def _check_fps(prev_time):
        """
        Prints the number of frames per second
        using the time elapsed since prevTime.
        
        :param prev_time:
        :type prev_time: time object
        :returns: The new time
        :rtype: time object
        """
        fps = 1/(time.time() - prev_time)
        print("{} fps".format(fps))
        return time.time()
        
    def _check_teleportation(self, frame, silhouette):
        """
        Check if the mouse moved too much, which would indicate an issue with the tracking
        notably the fitting in the past. If so, call self._stream.stopRecording() and raise
        EOFError.
        
        :param frame: The current frame (to be saved for troubleshooting if teleportation occured)
        :type frame: video_frame.Frame
        :param silhouette: The binary mask of the current frame\
         (to be saved for troubleshooting if teleportation occured)
        :type silhouette: video_frame.Frame
        
        :raises: EOFError if the mouse teleported
        """
        if len(self.positions) < 2:
            return
        last_vector = np.abs(np.array(self.positions[-1]) - np.array(self.positions[-2]))
        if (last_vector > self.teleportation_threshold).any():
            silhouette.save('teleportingSilhouette.tif')
            frame.save('teleportingFrame.tif')
            err_msg = 'Frame: {}, mouse teleported from {} to {}'\
                .format(self._stream.current_frame_idx, *self.positions[-2:])
            err_msg += '\nPlease see teleportingSilhouette.tif and teleportingFrame.tif for debugging'
            self._stream.stop_recording(err_msg)
            raise EOFError('End of recording reached')

    def __all_contour_points_in_roi(self, contour):
        for p in contour:
            if not self.tracking_region_roi.point_in_roi(tuple(p[0])):  # at least one point outside of ROI
                return False
        return True

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
                    if closed_contour and self.__all_contour_points_in_roi(cnt):
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
            frame = frame.normalise(self.bg_avg_avg)
        diff = Frame(cv2.absdiff(frame, self.bg))
        if self.bg_std is not None:
            threshold = self.bg_std * self.n_sds
            silhouette = diff > threshold
            silhouette = silhouette.astype(np.uint8) * 255
        else:
            diff = diff.astype(np.uint8)
            silhouette = diff.threshold(self.threshold)
        if self.clear_borders:
            silhouette.clear_borders()
        return silhouette, diff


class GuiTracker(Tracker):
    """
    A subclass of Tracker that reimplements trackFrame for use with the GUI
    This class implements read() to behave as a stream
    """
    def __init__(self, ui_iface, src_file_path=None, dest_file_path=None,
                 threshold=20, min_area=100, max_area=5000,
                 teleportation_threshold=10,
                 bg_start=0, track_from=1, track_to=None,
                 n_background_frames=1, n_sds=5.0,
                 clear_borders=False, normalise=False,
                 plot=False, fast=False, extract_arena=False,
                 camera_calibration=None,
                 callback=None):
        """
        :param TrackerInterface ui_iface: the interface this tracker is called from
        
        For the other parameters, see Tracker
        """
        Tracker.__init__(self, src_file_path=src_file_path, dest_file_path=dest_file_path,
                         threshold=threshold, min_area=min_area, max_area=max_area,
                         teleportation_threshold=teleportation_threshold,
                         bg_start=bg_start, track_from=track_from, track_to=track_to,
                         n_background_frames=n_background_frames, n_sds=n_sds,
                         clear_borders=clear_borders, normalise=normalise,
                         plot=plot, fast=fast, extract_arena=extract_arena,
                         camera_calibration=camera_calibration,
                         callback=callback)
        self.ui_iface = ui_iface
        self.current_frame_idx = 0
        self.record = dest_file_path is not None
    
    def set_roi(self, roi):
        """Set the region of interest and enable it"""
        self.roi = roi
        if roi is not None:
            self._make_bottom_square()

    def set_tracking_region_roi(self, roi):
        self.tracking_region_roi = roi

    def read(self):
        """
        The required method to behave as a video stream
        It calls self.track() and increments the current_frame_idx
        It also updates the uiIface positions accordingly
        """
        try:
            self.current_frame_idx = self._stream.current_frame_idx + 1
            result = self.track_frame(record=self.record, requested_output=self.ui_iface.output_type)
        except EOFError:
            self.ui_iface._stop('End of recording reached')
            return
        except cv2.error as e:
            self.ui_iface.timer.stop()
            self._stream.stop_recording('Error {} stopped recording'.format(e))
            return
        if result is not None:
            img, position, distances = result
            self.ui_iface.positions.append(position)
            self.ui_iface.distances_from_arena.append(distances)
            return img
        else:
            self.ui_iface.positions.append(self.default_pos)
            self.ui_iface.distances_from_arena.append(self.default_pos)
    
    def track_frame(self, record=False, requested_output='raw'):
        """
        Reimplementation of Tracker.trackFrame for the GUI
        """
        try:
            frame = self._stream.read()
            if self.camera_calibration is not None:
                frame = Frame(self.camera_calibration.remap(frame))
            fid = self._stream.current_frame_idx
            if self.track_to and (fid > self.track_to):
                raise KeyboardInterrupt  # stop recording
                
            if fid < self._stream.bg_start_frame:
                return frame.color(), self.default_pos, self.default_pos  # Skip junk frames
            elif self._stream.is_bg_frame():
                self._build_bg(frame)
                if record: self._stream._save(frame)
                return frame.color(), self.default_pos, self.default_pos
            elif self._stream.bg_end_frame < fid < self.track_from:
                if record: self._stream._save(frame)
                return frame.color(), self.default_pos, self.default_pos  # Skip junk frames
            else:  # Tracked frame
                if fid == self.track_from: self._finalise_bg()
                contour_found, sil = self._track_frame(frame, 'b', requested_output=requested_output)
                self.silhouette = sil.copy()
                if not contour_found:
                    if record: self._stream._save(frame)
                    write_structure_not_found_msg(self.silhouette, self.silhouette.shape[:2], self.current_frame_idx)
                    return self.silhouette, self.default_pos, self.default_pos  # Skip if no contour found

                if self.roi is not None: self._check_mouse_in_roi()
                self.paint(self.silhouette, 'c')
                self.silhouette.paint(curve=self.positions)
                if record: self._stream._save(self.silhouette)
                result = [self.silhouette, self.positions[-1]]
                if self.extract_arena:
                    distances = (self._get_distance_from_arena_center(), self._get_distance_from_arena_border())
                    self.distances_from_arena.append(distances)
                    result.append(self.distances_from_arena[-1])
                else:
                    result.append(self.default_pos)
                return result
        except VideoStreamFrameException as e:
            print('Error with video_stream at frame {}: \n{}'.format(fid, e))
        except (KeyboardInterrupt, EOFError) as e:
            msg = "Recording stopped by user" if (type(e) == KeyboardInterrupt) else str(e)
            self._stream.stop_recording(msg)
            raise EOFError
