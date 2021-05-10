"""
This is module contains the StructureTracker class.
A tracked structure is an object or group of objects with the same identity and tracking parameters.
This can be the specimen or it can be a set elements in the field of view that share the same detection parameters.
"""
import cv2
import numpy as np

from pyper.utilities import utils
from pyper.video.video_frame import update_img, Frame
from pyper.video.video_stream import IS_PI
from pyper.tracking.multi_results import MultiResults
from pyper.contours.contours_manager import ContoursManager


class StructureTracker(object):
    """
    Corresponds to the tracker of 1 structure with potentially several parts (e.g. structure=red cubes, where there
    are 3 cubes)
    """
    def __init__(self, name, main_params, thresholding_params, arena=None, stream=None, background=None):  # FIXME: plot color option to differentiate
        self.name = name
        self.params = main_params
        self.thresholding_params = thresholding_params
        self.multi_results = MultiResults(main_params, thresholding_params)
        self.contours_handler = ContoursManager(None, thresholding_params.n_structures_max)
        self.mask = None  # np.emtpy(), but not necessary as will use first frame shape

        self._stream = stream
        self.bg = background

        self.arena = arena
        self.roi = None
        self.tracking_region_roi = None
        self.measure_roi = None
        self.bottom_square = None

    def reset(self):
        self.multi_results.reset()
        # TODO: see if reset self.contour_handler ...

    def check_specimen_in_roi(self):
        """
        Checks whether the specimen is within the specified ROI and
        calls the specified callback method if so.
        """
        if self.roi is not None:
            if self.multi_results.last_pos_is_default():
                return
            for i, pos in enumerate([res.get_last_position() for res in self.multi_results.results]):
                if self.roi.contains_point(pos):
                    self.handle_object_in_tracking_roi(i)
                    self.mask = self.mask.copy()  # OPTIMISE:  # FIXME: why here

    def handle_object_in_tracking_roi(self, struct_idx):  # REFACTOR: part of roi add Callback class with call method
        """
        The method called when the specimen is found in the roi.
        This method is meant to be overwritten in subclasses of Tracker.
        """
        self.multi_results.results[struct_idx].overwrite_last_in_tracking_roi(True)
        self.bottom_square.frame = self.mask
        self.bottom_square.draw()

    def measure_callback(self, frame):  # REFACTOR: part of roi
        if self.measure_roi is not None:
            mask = self.measure_roi.to_mask(frame)
            values = np.extract(mask, frame)
            return values.mean()
        else:
            return [float('NaN')] * self.thresholding_params.n_structures_max

    def set_default_results(self):
        # if self.params.infer_location:  # TODO@: implement
        #     self.multi_results.repeat_last()  # TODO: if infer put negative value and interpolate later
        # else:
        self.multi_results.append_defaults()

    def paint_rois(self, frame, roi_color='y', arena_color='m'):
        if self.roi is not None:
            self.roi.contour.set_params(frame, contour_type='raw', color=roi_color, line_thickness=2)
            self.roi.contour.draw()
        if self.params.extract_arena:
            self.arena.contour.set_params(frame, contour_type='raw', color=arena_color, line_thickness=2)
            self.arena.contour.draw()

    def paint_frame(self, frame_idx):  # FIXME: signature
        """
        Displays the current frame with the trajectory of the specimen and potentially the ROI and the
        Arena ROI if these have been specified.
        """
        if self.params.plot:
            self.paint_rois(self.mask)
            curves = [res.plotting_positions() for res in self.multi_results.results]
            self.mask.display(win_name='Diff', text='Frame: {}'.format(frame_idx),
                              curve=curves)

    def _draw_subregion_roi(self, img, color='y'):  # TODO: just update contour w/ img
        if self.tracking_region_roi is not None:
            self.tracking_region_roi.contour.set_params(img, color=color)
            self.tracking_region_roi.contour.draw()

    def track_frame(self, frame, requested_color='r', requested_output='raw'):
        """
        Get the position of the specimen in frame and append to self.multi_results
        Returns the mask of the current frame with the specimen potentially drawn

        :param video_frame.Frame frame: The video frame to use.
        :param str requested_color: A character (for list of supported characters see ObjectContour)\
         indicating the color to draw the contour
        :param str requested_output: Which frame type to output (one of ['raw', 'mask', 'diff'])
        :returns: mask
        :rtype: binary mask or None
        """
        processed_frame = self._pre_process_frame(frame)  # FIXME: check why frame is float32
        mask, diff = self.get_mask(processed_frame)
        update_img(self.mask, mask)
        self.contours_handler.update(mask)
        if not self.contours_handler.contours:
            contours = None
        else:
            contours = self.contours_handler.get_in_range(self.thresholding_params.min_area,
                                                          self.thresholding_params.max_area,
                                                          self.thresholding_params.n_structures_max,
                                                          check_in_roi=self.tracking_region_roi)

        if IS_PI and self.params.fast:
            requested_output = 'mask'
        plot_silhouette, color_is_default = self._get_plot_silhouette(requested_output, frame, diff, mask)
        color = 'w' if color_is_default else requested_color

        contour_found = bool(contours)
        if contour_found:
            contours.set_params(frame=plot_silhouette, contour_type='raw', color=color)
            if self.params.plot:
                contours.draw()  # even if wrong size to help spot issues
                self._draw_subregion_roi(plot_silhouette)

            self.multi_results.multi_update(self.arena, contours, self.measure_callback(frame))
            err_msg = self.multi_results.check_teleportation(frame, mask, self._stream.current_frame_idx)
            if err_msg:
                self._stream.stop_recording(err_msg)
                raise EOFError(err_msg)
        else:
            print("No contour found")
            if self.contours_handler.not_in_range:
                self._handle_bad_size_contour(plot_silhouette)
            self._fast_print('Frame {}, no contour found'.format(self._stream.current_frame_idx))
        return contour_found, plot_silhouette

    def _pre_process_frame(self, frame):
        treated_frame = frame.gray(self.params.fast)   # TODO: check if we should separate setting
        if not self.params.fast:
            treated_frame = treated_frame.denoise().blur()
        return treated_frame

    def get_mask(self, frame):
        """
        Get the binary mask (8bits) of the specimen
        from the thresholded difference between frame and the background

        :param video_frame.Frame frame: The current frame to analyse
        :returns: mask (the binary mask), diff (the grayscale optimised for thresholding)
        :rtype: tuple(video_frame.Frame, video_frame.Frame)
        """
        if self.params.normalise:
            frame = frame.normalise(self.bg.global_avg)
        diff = self.bg.diff(frame)
        if self.bg.use_sd:
            threshold = self.bg.get_std_threshold()
            mask = diff > threshold
            mask = mask.astype(np.uint8) * 255
        else:
            diff = diff.astype(np.uint8)  # OPTIMISE
            mask = diff.threshold(self.params.detection_threshold)  # FIXME: !=
        mask = self._post_process_mask(mask)
        return mask, diff

    def _post_process_mask(self, mask):
        if self.params.n_erosions:
            mask = mask.erode(self.params.n_erosions)
        if self.params.clear_borders:
            mask.clear_borders()
        return mask

    def _handle_bad_size_contour(self, img):
        area = self.contours_handler.get_biggest_area()
        if not area:
            print("FIXME: no contour found")  # FIXME:
            return
        if area > self.thresholding_params.max_area:
            msg = 'Biggest structure too big ({} > {})'.format(area, self.thresholding_params.max_area)
        else:
            msg = 'Biggest structure too small ({} < {})'.format(area, self.thresholding_params.min_area)
        self._fast_print(msg)
        if self.params.plot and img is not None:
            utils.write_structure_size_incorrect_msg(img, img.shape[:2], msg)

    def _fast_print(self, in_str):
        """
        Print only if `fast` option not selected

        :param str in_str: The string to print
        :return:
        """
        if not self.params.fast:
            print(in_str)

    def _get_plot_silhouette(self, requested_output, frame, diff, mask):  # OPTIMISE:
        color_is_default = False
        if self.params.plot:
            if requested_output == 'raw':
                plot_silhouette = frame.color(in_place=True)
            elif requested_output == 'diff':
                plot_silhouette = diff.color(in_place=True)
            elif requested_output == 'mask':
                plot_silhouette = mask
                color_is_default = True
            else:
                raise NotImplementedError("Expected one of ('raw', 'mask', 'diff') "
                                          "for requested_output, got: {}".format(requested_output))
        else:
            color_is_default = True
            plot_silhouette = frame
        return plot_silhouette, color_is_default


class StructureTrackerGui(StructureTracker):

    def paint_frame(self, frame, should_update_vid):  # WARNING: different signature as parent  + WARNING: in place
        """
        Prepare the current frame for display.
        For optimisation purposes, this will only occur on a defined fraction (max each)
        of the frames

        :param bool should_update_vid: Whether this frame should be displayed (for speed purposes)
        :return:
        """
        self.paint_rois(frame, roi_color='c')
        if should_update_vid:  # do only every x pnts in fast mode
            frame.paint(curve=(self.multi_results.plotting_positions()))


class ColorStructureTracker(StructureTrackerGui):
    def _pre_process_frame(self, frame):
        return cv2.blur(frame, (5, 5))

    def get_mask(self, frame):
        mask = cv2.inRange(frame,
                           np.array(self.thresholding_params.min_threshold),  # FIXME: OPTIMISE: cast once and for all
                           np.array(self.thresholding_params.max_threshold))
        mask = Frame(mask)
        mask = self._post_process_mask(mask)
        diff = Frame(frame.copy())
        return mask, diff
    # self.opened_mask[:] = cv2.morphologyEx(self.maskMouse, cv2.MORPH_OPEN,
    #                                        self._args["segmentation"]["kernel"],
    #                                        iterations=struct_params.binary_iterations)  # despeckle
    # self.closed_mask[:] = cv2.morphologyEx(self.openingMouse, cv2.MORPH_CLOSE,
    #                                        self._args["segmentation"]["kernel"],
    #                                        iterations=struct_params.binary_iterations)  # large object filling


class HsvStructureTracker(ColorStructureTracker):
    def _pre_process_frame(self, frame):
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # TODO: optimise by avoiding copies + try skimage version
        return cv2.blur(hsv_frame, (5, 5))
