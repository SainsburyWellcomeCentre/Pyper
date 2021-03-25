import numpy as np

from pyper.video.video_frame import Frame
from pyper.gui.gui_tracker import GuiTracker


class PupilGuiTracker(GuiTracker):
    """
    A subclass of GuiTracker with processing optimised
    to track the pupil of an animal
    """
    WHITE_FRAME = None

    def _pre_process_frame(self, frame):
        treated_frame = Frame(frame.gray().astype(np.uint8))
        # if not IS_PI and not self.params.fast:
        #     treated_frame = treated_frame.denoise(3).blur(3)
        treated_frame = treated_frame.blur(1)
        return treated_frame

    def _get_silhouette(self, frame):
        """
        Get the binary mask (8bits) of the pupil
        from the thresholded difference between frame and the background

        :param frame: The current frame to analyse
        :type frame: video_frame.Frame

        :returns: silhouette (the binary mask)
        :rtype: video_frame.Frame
        """
        if PupilGuiTracker.WHITE_FRAME is None:
            PupilGuiTracker.WHITE_FRAME = np.full(frame.shape, 255, dtype=np.uint8)

        if self.params.normalise:
            frame = frame.normalise(self.bg.global_avg)
        # diff = Frame(cv2.absdiff(frame, self.bg))
        diff = Frame(PupilGuiTracker.WHITE_FRAME - frame)  # Negative

        if self.bg.use_sd:
            threshold = self.bg.get_std_threshold()
            silhouette = diff > threshold
            silhouette = silhouette.astype(np.uint8) * 255
        else:
            diff = diff.astype(np.uint8)
            silhouette = diff.threshold(self.params.detection_threshold)
        if self.params.clear_borders:
            silhouette.clearBorders()
        return silhouette, diff

