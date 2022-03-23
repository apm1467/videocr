from __future__ import annotations
import os
from loguru import logger
from typing import List
import sys
from typing import List

import cv2
import easyocr
import numpy as np

from . import constants
from . import utils
from .utils import batcher, plot_ocr
from .models import PredictedFrame, PredictedSubtitle
from .opencv_adapter import Capture

BATCHSIZE = 32

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

    def run_ocr(
        self,
        lang: str,
        time_start: str,
        time_end: str,
        conf_threshold: int,
        tesseract_config: str,
        roi=[[0, 1], [0, 1]],
        debug=bool,
        num_jobs=int,
    ) -> None:
        self.lang = lang
        self.tesseract_config = tesseract_config
        self.roi = roi
        self.debug = debug
        self.num_jobs = num_jobs

        ocr_start = utils.get_frame_index(time_start, self.fps) if time_start else 0
        ocr_end = (
            utils.get_frame_index(time_end, self.fps) if time_end else self.num_frames
        )

        if ocr_end < ocr_start:
            raise ValueError("time_start is later than time_end")
        num_ocr_frames = ocr_end - ocr_start

        # get frames from ocr_start to ocr_end
        with Capture(self.path) as v:
            v.set(cv2.CAP_PROP_POS_FRAMES, ocr_start)
            self.reader = easyocr.Reader(["ch_tra", "en"])
            self.pred_frames = []
            for idx in tqdm(batcher(range(num_ocr_frames),
                                    batch_size=BATCHSIZE), total=num_ocr_frames//BATCHSIZE):
                frames = [v.read()[1] for _ in range(len(idx))]
                frames = np.stack(frames)
                data = self._image_to_data(idx, frames)
                for _idx, _data in zip(idx, data):
                    self.pred_frames.append(
                        PredictedFrame(_idx + ocr_start, _data,
                                       conf_threshold, easyocr=True))

    def _image_to_data(self, idx, img) -> str:
        roi_img = img[:,
            int(self.height*self.roi[1][0]):int(self.height*self.roi[1][1]),
            int(self.width*self.roi[0][0]):int(self.width*self.roi[0][1])
        ]
        result = self.reader.readtext_batched(roi_img, batch_size=BATCHSIZE,
                                              paragraph=True)
        if self.debug:
            for _idx, img, _result in zip(idx, roi_img, result):
                cv2.imwrite(f"{_idx}.jpg", img)
        return result

    def get_subtitles(self, sim_threshold: int) -> str:
        self._generate_subtitles(sim_threshold)
        return "".join(
            "{}\n{} --> {}\n{}\n\n".format(
                i,
                utils.get_srt_timestamp(sub.index_start, self.fps),
                utils.get_srt_timestamp(sub.index_end, self.fps),
                sub.text,
            )
            for i, sub in enumerate(self.pred_subs)
        )

    def _generate_subtitles(self, sim_threshold: int) -> None:
        self.pred_subs = []

        if self.pred_frames is None:
            raise AttributeError(
                "Please call self.run_ocr() first to perform ocr on frames"
            )

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
                    PredictedSubtitle(self.pred_frames[i:para_new], sim_threshold)
                )
                i = para_new
                j = i
                bound = WIN_BOUND

            j += 1

        # also handle the last remaining frames
        if i < len(self.pred_frames) - 1:
            self._append_sub(PredictedSubtitle(self.pred_frames[i:], sim_threshold))

    def _append_sub(self, sub: PredictedSubtitle) -> None:
        if len(sub.text) == 0:
            return

        # merge new sub to the last subs if they are similar
        while self.pred_subs and sub.is_similar_to(self.pred_subs[-1]):
            ls = self.pred_subs[-1]
            del self.pred_subs[-1]
            sub = PredictedSubtitle(ls.frames + sub.frames, sub.sim_threshold)

        self.pred_subs.append(sub)
