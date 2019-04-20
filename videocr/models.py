from __future__ import annotations
from typing import List
from dataclasses import dataclass


CONFIDENCE_THRESHOLD = 60
# predictions with lower confidence will be filtered out


@dataclass
class PredictedWord:
    __slots__ = 'confidence', 'text'
    confidence: int
    text: str


class PredictedFrame:
    words: List[PredictedWord]

    def __init__(self, pred_data: str):
        self.words = []

        block_current = 1
        for line in pred_data.split('\n')[1:]:
            tmp = line.split()
            if len(tmp) < 12:
                # no word is predicted
                continue
            _, _, block_num, *_, conf, text = tmp
            block_num, conf = int(block_num), int(conf)

            # handle line breaks
            if block_current < block_num:
                block_current = block_num
                self.words.append(PredictedWord(0, '\n'))

            if conf >= CONFIDENCE_THRESHOLD:
                self.words.append(PredictedWord(conf, text))

    @property
    def confidence(self) -> int:
        return sum(word.confidence for word in self.words)

    @property
    def text(self) -> str:
        return ''.join(word.text + ' ' for word in self.words)

