from __future__ import annotations
from concurrent import futures
import pytesseract
import cv2
import timeit

from .models import PredictedFrame


class Video:
    path: str
    lang: str
    num_frames: int

    def __init__(self, path, lang):
        self.path = path
        self.lang = lang
        v = cv2.VideoCapture(path)
        self.num_frames = int(v.get(cv2.CAP_PROP_FRAME_COUNT))
        v.release()

    def _frame_ocr(self, img):
        data = pytesseract.image_to_data(img, lang=self.lang)
        return data

    def run_ocr(self):
        v = cv2.VideoCapture(self.path)
        print(self.num_frames)
        frames = (v.read()[1] for _ in range(40))

        with futures.ProcessPoolExecutor() as pool:
            frames_ocr = pool.map(self._frame_ocr, frames, chunksize=1)
            for i, data in enumerate(frames_ocr):
                pred = PredictedFrame(i, data)
                print(pred.text)

        v.release()


time_start = timeit.default_timer()
v = Video('1.mp4', 'HanS')
v.run_ocr()
time_stop = timeit.default_timer()
print(time_stop - time_start)
