from __future__ import annotations
from concurrent import futures
import datetime
import pytesseract
import cv2

from . import constants
from .models import PredictedFrame, PredictedSubtitle


class Video:
    path: str
    lang: str
    use_fullframe: bool
    num_frames: int
    fps: float
    height: int
    pred_frames: List[PredictedFrame]
    pred_subs: List[PredictedSubtitle]

    def __init__(self, path: str):
        self.path = path
        v = cv2.VideoCapture(path)
        if not v.isOpened():
            raise IOError('can not open video format {}'.format(path))
        self.num_frames = int(v.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = v.get(cv2.CAP_PROP_FPS)
        self.height = int(v.get(cv2.CAP_PROP_FRAME_HEIGHT))
        v.release()

    def run_ocr(self, lang: str, time_start: str, time_end: str,
                conf_threshold: int, use_fullframe: bool) -> None:
        self.lang = lang
        self.use_fullframe = use_fullframe

        ocr_start = self._frame_index(time_start) if time_start else 0
        ocr_end = self._frame_index(time_end) if time_end else self.num_frames

        if ocr_end < ocr_start:
            raise ValueError('time_start is later than time_end')
        num_ocr_frames = ocr_end - ocr_start

        # get frames from ocr_start to ocr_end
        v = cv2.VideoCapture(self.path)
        v.set(cv2.CAP_PROP_POS_FRAMES, ocr_start)
        frames = (v.read()[1] for _ in range(num_ocr_frames))

        # perform ocr to frames in parallel
        with futures.ProcessPoolExecutor() as pool:
            ocr_map = pool.map(self._single_frame_ocr, frames, chunksize=10)
            self.pred_frames = [
                PredictedFrame(i + ocr_start, data, conf_threshold) 
                for i, data in enumerate(ocr_map)]

        v.release()

    # convert time str to frame index
    def _frame_index(self, time: str) -> int:
        t = time.split(':')
        t = list(map(float, t))
        if len(t) == 3:
            td = datetime.timedelta(hours=t[0], minutes=t[1], seconds=t[2])
        elif len(t) == 2:
            td = datetime.timedelta(minutes=t[0], seconds=t[1])
        else:
            raise ValueError(
                'time data "{}" does not match format "%H:%M:%S"'.format(time))

        index = int(td.total_seconds() * self.fps)
        if index > self.num_frames or index < 0:
            raise ValueError(
                'time data "{}" exceeds video duration'.format(time))

        return index

    def _single_frame_ocr(self, img) -> str:
        if not self.use_fullframe:
            # only use bottom half of the frame by default
            img = img[self.height // 2:, :]
        config = '--tessdata-dir "{}"'.format(constants.TESSDATA_DIR)
        return pytesseract.image_to_data(img, lang=self.lang, config=config)

    def get_subtitles(self) -> str:
        self._generate_subtitles()
        return ''.join(
            '{}\n{} --> {}\n{}\n\n'.format(
                i,
                self._srt_timestamp(sub.index_start),
                self._srt_timestamp(sub.index_end),
                sub.text)
            for i, sub in enumerate(self.pred_subs))

    def _generate_subtitles(self) -> None:
        self.pred_subs = []

        if self.pred_frames is None:
            raise AttributeError(
                'Please call self.run_ocr() first to perform ocr on frames')

        # divide ocr of frames into subtitle paragraphs using sliding window
        WIN_BOUND = int(self.fps // 2)  # 1/2 sec sliding window boundary
        bound = WIN_BOUND
        i = 0
        j = 1
        while j < len(self.pred_frames):
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

        # also handle the last remaining frames
        if i < len(self.pred_frames) - 1:
            self._append_sub(PredictedSubtitle(self.pred_frames[i:]))

    def _append_sub(self, sub: PredictedSubtitle) -> None:
        if len(sub.text) == 0:
            return

        # merge new sub to the last subs if they are similar
        while self.pred_subs and sub.is_similar_to(self.pred_subs[-1]):
            ls = self.pred_subs[-1]
            del self.pred_subs[-1]
            sub = PredictedSubtitle(ls.frames + sub.frames)

        self.pred_subs.append(sub)

    def _srt_timestamp(self, frame_index: int) -> str:
        td = datetime.timedelta(seconds=frame_index / self.fps)
        ms = td.microseconds // 1000
        m, s = divmod(td.seconds, 60)
        h, m = divmod(m, 60)
        return '{:02d}:{:02d}:{:02d},{:03d}'.format(h, m, s, ms)
