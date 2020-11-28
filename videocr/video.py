from __future__ import annotations
from typing import List
import sys
import p_tqdm
import pytesseract
import cv2

from . import constants
from . import utils
from .models import PredictedFrame, PredictedSubtitle
from .opencv_adapter import Capture


class Video:
    path: str
    lang: str
    num_frames: int
    fps: float
    height: int
    pred_frames: List[PredictedFrame]
    pred_subs: List[PredictedSubtitle]

    def __init__(self, path: str):
        self.path = path
        with Capture(path) as v:
            self.num_frames = int(v.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = v.get(cv2.CAP_PROP_FPS)
            self.height = int(v.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.width = int(v.get(cv2.CAP_PROP_FRAME_WIDTH))

    def run_ocr(self, lang: str, time_start: str, time_end: str,
                conf_threshold: int, tesseract_config: str, roi=[[0, 1], [0, 1]], debug=bool, num_jobs=int) -> None:
        self.lang = lang
        self.tesseract_config = tesseract_config
        self.roi = roi
        self.debug = debug
        self.num_jobs = num_jobs

        ocr_start = utils.get_frame_index(
            time_start, self.fps) if time_start else 0
        ocr_end = utils.get_frame_index(
            time_end, self.fps) if time_end else self.num_frames

        if ocr_end < ocr_start:
            raise ValueError('time_start is later than time_end')
        num_ocr_frames = ocr_end - ocr_start

        # get frames from ocr_start to ocr_end
        with Capture(self.path) as v:
            v.set(cv2.CAP_PROP_POS_FRAMES, ocr_start)
            frames = (v.read()[1] for _ in range(num_ocr_frames))

            # perform ocr to frames in parallel
            if num_jobs is not None:
                it_ocr = p_tqdm.p_imap(self._image_to_data,
                                       range(num_ocr_frames), frames, num_cpus=num_jobs)
            else:
                it_ocr = p_tqdm.p_imap(self._image_to_data,
                                       range(num_ocr_frames), frames)

            self.pred_frames = [
                PredictedFrame(i + ocr_start, data, conf_threshold)
                for i, data in enumerate(it_ocr)
            ]

    def _image_to_data(self, idx, img) -> str:
        roi_img = img[
            int(self.height*self.roi[1][0]):int(self.height*self.roi[1][1]),
            int(self.width*self.roi[0][0]):int(self.width*self.roi[0][1])
        ]
        config = f'{self.tesseract_config} --tessdata-dir "{constants.TESSDATA_DIR}"'
        if self.debug:
            cv2.imwrite(f"{idx}.jpg", roi_img)
        try:
            return pytesseract.image_to_data(roi_img, lang=self.lang, config=config)
        except Exception as e:
            sys.exit('{}: {}'.format(e.__class__.__name__, e))

    def get_subtitles(self, sim_threshold: int) -> str:
        self._generate_subtitles(sim_threshold)
        return ''.join(
            '{}\n{} --> {}\n{}\n\n'.format(
                i,
                utils.get_srt_timestamp(sub.index_start, self.fps),
                utils.get_srt_timestamp(sub.index_end, self.fps),
                sub.text)
            for i, sub in enumerate(self.pred_subs))

    def _generate_subtitles(self, sim_threshold: int) -> None:
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
                self._append_sub(PredictedSubtitle(
                    self.pred_frames[i:para_new], sim_threshold))
                i = para_new
                j = i
                bound = WIN_BOUND

            j += 1

        # also handle the last remaining frames
        if i < len(self.pred_frames) - 1:
            self._append_sub(PredictedSubtitle(
                self.pred_frames[i:], sim_threshold))

    def _append_sub(self, sub: PredictedSubtitle) -> None:
        if len(sub.text) == 0:
            return

        # merge new sub to the last subs if they are similar
        while self.pred_subs and sub.is_similar_to(self.pred_subs[-1]):
            ls = self.pred_subs[-1]
            del self.pred_subs[-1]
            sub = PredictedSubtitle(ls.frames + sub.frames, sub.sim_threshold)

        self.pred_subs.append(sub)
