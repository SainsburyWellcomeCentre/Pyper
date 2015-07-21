import numpy as np
from scipy.misc import imresize
import cv2
from cv2 import cv

from video_stream import RecordedVideoStream

from progressbar import Percentage, Bar,  ProgressBar

class Transcoder(RecordedVideoStream):
    def __init__(self, srcFilePath, destFilePath, bgStart, nBackgroundFrames, cropParams, scaleParams):
        RecordedVideoStream.__init__(self, srcFilePath, bgStart, nBackgroundFrames)
        self.cropParams = np.array(cropParams)
        self.scaleParams = np.array(scaleParams)
        size = self.getFinalSize()
        self.videoWriter = cv2.VideoWriter(destFilePath,
                                    cv.CV_FOURCC(*'mp4v'),
                                    self.fps,
                                    size[::-1],
                                    True)
    
    def getFinalSize(self):
        croppedWidth = self.size[0] - sum(self.cropParams[0])
        croppedHeight = self.size[1] - sum(self.cropParams[1])
        croppedSize = np.array((croppedWidth, croppedHeight))

        finalSize = croppedSize * self.scaleParams
        finalSize = tuple(finalSize.astype(np.uint32))
        return finalSize
    
    def transcode(self):
        cropParams = self.cropParams
        finalWidth, finalHeight = self.getFinalSize()
        print('Final size: {},  {}'.format(finalWidth, finalHeight))
        widgets=['Encoding Progress: ', Percentage(), Bar()]
        pbar = ProgressBar(widgets=widgets, maxval=self.nFrames).start()
        for i in range(self.nFrames):
            pbar.update(i)
            frame = self.read()
            frame = frame[cropParams[0][0]: -cropParams[0][1],  cropParams[1][0]: -cropParams[1][1]]
            scale = np.concatenate((self.scaleParams, np.array([1]))) * frame.shape
            frame = imresize(frame, scale.astype(int), interp='bilinear')
            self.videoWriter.write(frame)
#            self.videoWriter.write(np.uint8(np.dstack([frame]*3)))
        pbar.finish()
        self.videoWriter.release()
        self.videoWriter = None
