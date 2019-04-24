from __future__ import annotations
from typing import List
from dataclasses import dataclass


CONF_THRESHOLD = 60
# word predictions with lower confidence will be filtered out


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

    def __init__(self, index, pred_data: str):
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
                self.words.append(PredictedWord(0, '\n'))

            if conf >= CONF_THRESHOLD:
                self.words.append(PredictedWord(conf, text))

        self.confidence = sum(word.confidence for word in self.words)
        self.text = ''.join(word.text + ' ' for word in self.words).strip()

