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

    def get_mask(self, frame):
        """
        Get the binary mask (8bits) of the pupil
        from the thresholded difference between frame and the background

        :param video_frame.Frame frame: The current frame to analyse
        :returns: mask (the binary mask)
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
            mask = diff > threshold
            mask = mask.astype(np.uint8) * 255
        else:
            diff = diff.astype(np.uint8)
            mask = diff.threshold(self.params.detection_threshold)
        if self.params.clear_borders:
            mask.clearBorders()
        return mask, diff

