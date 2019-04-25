from __future__ import annotations
from concurrent import futures
import datetime
import pytesseract
import cv2
import timeit

from .models import PredictedFrame, PredictedSubtitle


class Video:
    path: str
    lang: str
    use_fullframe: bool
    num_frames: int
    fps: float
    pred_frames: List[PredictedFrame]
    pred_subs: List[PredictedSubtitle]

    def __init__(self, path, lang, use_fullframe=False):
        self.path = path
        self.lang = lang
        self.use_fullframe = use_fullframe
        v = cv2.VideoCapture(path)
        self.num_frames = int(v.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = v.get(cv2.CAP_PROP_FPS)
        v.release()

    def _single_frame_ocr(self, img) -> str:
        if not self.use_fullframe:
            # only use bottom half of the frame by default
            img = img[img.shape[0] // 2:, :]
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

        self.pred_subs = []

        # divide ocr of frames into subtitle paragraphs using sliding window
        WIN_BOUND = int(self.fps / 2)  # 1/2 sec sliding window boundary
        bound = WIN_BOUND
        i = 0
        j = 1
        while j < self.num_frames:
            fi, fj = self.pred_frames[i], self.pred_frames[j]

            if fi.is_similar_to(fj):
                bound = WIN_BOUND
            elif bound > 0:
                bound -= 1
            else:
                # divide subtitle paragraphs
                para_new = j - WIN_BOUND
                self._append_sub(
                    PredictedSubtitle(self.pred_frames[i:para_new]))
                i = para_new
                j = i
                bound = WIN_BOUND

            j += 1

        if i < self.num_frames - 1:
            self._append_sub(PredictedSubtitle(self.pred_frames[i:]))

        for i, sub in enumerate(self.pred_subs):
            print('{}\n{} --> {}\n{}\n'.format(
                i,
                self._srt_timestamp(sub.index_start),
                self._srt_timestamp(sub.index_end),
                sub.text))

        return ''

    def _append_sub(self, sub: PredictedSubtitle) -> None:
        if len(sub.text) == 0:
            return

        # merge new sub to the last subs if they are similar
        while self.pred_subs and sub.is_similar_to(self.pred_subs[-1]):
            lsub = self.pred_subs[-1]
            del self.pred_subs[-1]
            sub = PredictedSubtitle(lsub.frames + sub.frames)

        self.pred_subs.append(sub)

    def _srt_timestamp(self, frame_index) -> str:
        time = str(datetime.timedelta(seconds=frame_index / self.fps))
        return time.replace('.', ',')  # srt uses comma as fractional separator


time_start = timeit.default_timer()
v = Video('1.mp4', 'HanS')
v.run_ocr()
time_stop = timeit.default_timer()
print('time for ocr: ', time_stop - time_start)

time_start = timeit.default_timer()
v.get_subtitles()
time_stop = timeit.default_timer()
print('time for get sub: ', time_stop - time_start)
