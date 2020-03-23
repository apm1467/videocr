from __future__ import annotations
from typing import List
from dataclasses import dataclass
from rapidfuzz import fuzz


@dataclass
class PredictedWord:
    __slots__ = 'confidence', 'text'
    confidence: int
    text: str


class PredictedFrame:
    index: int  # 0-based index of the frame
    words: List[PredictedWord]
    confidence: int  # total confidence of all words
    text: str

    def __init__(self, index: int, pred_data: str, conf_threshold: int):
        self.index = index
        self.words = []

        block = 0  # keep track of line breaks

        for l in pred_data.splitlines()[1:]:
            word_data = l.split()
            if len(word_data) < 12:
                # no word is predicted
                continue
            _, _, block_num, *_, conf, text = word_data
            block_num, conf = int(block_num), int(conf)

            # handle line breaks
            if block < block_num:
                block = block_num
                if self.words and self.words[-1].text != '\n':
                    self.words.append(PredictedWord(0, '\n'))

            # word predictions with low confidence will be filtered out
            if conf >= conf_threshold:
                self.words.append(PredictedWord(conf, text))

        self.confidence = sum(word.confidence for word in self.words)

        self.text = ' '.join(word.text for word in self.words)
        # remove chars that are obviously ocr errors
        table = str.maketrans('|', 'I', '<>{}[];`@#$%^*_=~\\')
        self.text = self.text.translate(table).replace(' \n ', '\n').strip()

    def is_similar_to(self, other: PredictedFrame, threshold=70) -> bool:
        return fuzz.ratio(self.text, other.text) >= threshold


class PredictedSubtitle:
    frames: List[PredictedFrame]
    sim_threshold: int
    text: str

    def __init__(self, frames: List[PredictedFrame], sim_threshold: int):
        self.frames = [f for f in frames if f.confidence > 0]
        self.sim_threshold = sim_threshold

        if self.frames:
            self.text = max(self.frames, key=lambda f: f.confidence).text
        else:
            self.text = ''

    @property
    def index_start(self) -> int:
        if self.frames:
            return self.frames[0].index
        return 0

    @property
    def index_end(self) -> int:
        if self.frames:
            return self.frames[-1].index
        return 0

    def is_similar_to(self, other: PredictedSubtitle) -> bool:
        return fuzz.partial_ratio(self.text, other.text) >= self.sim_threshold

    def __repr__(self):
        return '{} - {}. {}'.format(self.index_start, self.index_end, self.text)
