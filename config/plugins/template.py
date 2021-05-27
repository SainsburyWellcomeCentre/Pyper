import cv2
import numpy as np

from pyper.video.video_frame import Frame
from pyper.tracking.structure_tracker import StructureTrackerGui


class TemplateStructureTracker(StructureTrackerGui):

    def _pre_process_frame(self, frame):
        return cv2.blur(frame, (5, 5))

    def get_mask(self, frame):
        mask = cv2.inRange(frame,
                           np.array(self.thresholding_params.min_threshold),
                           np.array(self.thresholding_params.max_threshold))
        mask = Frame(mask)
        mask = self._post_process_mask(mask)
        diff = Frame(frame.copy())
        return mask, diff
