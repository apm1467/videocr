from __future__ import annotations
from concurrent import futures
import pytesseract
import cv2
import timeit

from .models import PredictedFrame, PredictedSubtitle


SUBTITLE_BOUND = 10


class Video:
    path: str
    lang: str
    num_frames: int
    pred_frames: List[PredictedFrame]

    def __init__(self, path, lang):
        self.path = path
        self.lang = lang
        v = cv2.VideoCapture(path)
        self.num_frames = int(v.get(cv2.CAP_PROP_FRAME_COUNT))
        v.release()

    def _single_frame_ocr(self, img) -> str:
        img = img[img.shape[0] // 2:, :]  # only use bottom half of the frame
        data = pytesseract.image_to_data(img, lang=self.lang)
        return data

    def run_ocr(self) -> None:
        v = cv2.VideoCapture(self.path)
        frames = (v.read()[1] for _ in range(self.num_frames))

        # perform ocr to all frames in parallel
        with futures.ProcessPoolExecutor() as pool:
            frames_ocr = pool.map(self._single_frame_ocr, frames, chunksize=10)
            self.pred_frames = [PredictedFrame(i, data) 
                                for i, data in enumerate(frames_ocr)]

        v.release()

    def get_subtitles(self) -> str:
        if self.pred_frames is None:
            raise AttributeError(
                'Please call self.run_ocr() first to generate ocr of frames')

        # divide ocr of frames into subtitle paragraphs using sliding window
        i = 0
        j = 1
        bound = SUBTITLE_BOUND
        while j < self.num_frames:
            fi, fj = self.pred_frames[i], self.pred_frames[j]

            if fi.is_similar_to(fj):
                bound = SUBTITLE_BOUND
            elif bound > 0:
                bound -= 1
            else:
                # divide subtitle paragraphs
                para_new = j - SUBTITLE_BOUND
                print(PredictedSubtitle(self.pred_frames[i:para_new]).text)
                i = para_new
                j = i
                bound = SUBTITLE_BOUND

            j += 1

        if i < self.num_frames - 1:
            print(PredictedSubtitle(self.pred_frames[i:]).text)

        return ''


time_start = timeit.default_timer()
v = Video('1.mp4', 'HanS')
v.run_ocr()
v.get_subtitles()
time_stop = timeit.default_timer()
print(time_stop - time_start)
