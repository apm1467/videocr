import datetime
import shutil
from urllib.request import urlopen

import numpy as np
from itertools import islice
import cv2
from . import constants
from loguru import logger

from typing import Tuple
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

# download language data files to ~/tessdata if necessary
def download_lang_data(lang: str):
    constants.TESSDATA_DIR.mkdir(parents=True, exist_ok=True)

    for lang_name in lang.split("+"):
        filepath = constants.TESSDATA_DIR / "{}.traineddata".format(lang_name)
        if not filepath.is_file():
            # download needed file
            if lang_name[0].isupper():
                url = constants.TESSDATA_SCRIPT_URL.format(lang_name)
            else:
                url = constants.TESSDATA_URL.format(lang_name)

            with urlopen(url) as res, open(filepath, "w+b") as f:
                shutil.copyfileobj(res, f)


# convert time string to frame index
def get_frame_index(time_str: str, fps: float):
    t = time_str.split(":")
    t = list(map(float, t))
    if len(t) == 3:
        td = datetime.timedelta(hours=t[0], minutes=t[1], seconds=t[2])
    elif len(t) == 2:
        td = datetime.timedelta(minutes=t[0], seconds=t[1])
    else:
        raise ValueError(
            'Time data "{}" does not match format "%H:%M:%S"'.format(time_str)
        )
    index = int(td.total_seconds() * fps)
    return index


# convert frame index into SRT timestamp
def get_srt_timestamp(frame_index: int, fps: float):
    td = datetime.timedelta(seconds=frame_index / fps)
    ms = td.microseconds // 1000
    m, s = divmod(td.seconds, 60)
    h, m = divmod(m, 60)
    return "{:02d}:{:02d}:{:02d},{:03d}".format(h, m, s, ms)

def batcher(iterable, batch_size):
    iterator = iter(iterable)
    while batch := list(islice(iterator, batch_size)):
        yield batch

def cv2_img_add_text(img, text, left_corner: Tuple[int, int],
                     text_rgb_color=(255, 0, 0), text_size=24, font='SourceHanSansTW-Medium.otf', **option):
    """
    USAGE:
        cv2_img_add_text(img, '中文', (0, 0), text_rgb_color=(0, 255, 0), text_size=12, font='mingliu.ttc')
    """
    img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    font_text = ImageFont.truetype(font=font, size=text_size, encoding=option.get('encoding', 'utf-8'))
    draw.text(left_corner, text, text_rgb_color, font=font_text)
    cv2_img = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)
    return cv2_img

def plot_ocr(img, ocr_result):
    font = cv2.FONT_HERSHEY_COMPLEX
    for _result in ocr_result:
        #box, text, conf = _result
        box, text = _result
        (x, y, x2, y2) = box[0][0], box[0][1], box[2][0], box[2][1]
        img = cv2.rectangle(img, (x, y), (x2, y2), (0, 255, 0), 2)
        #img = cv2.putText(img, text, (x, y2), font, 2,(255,255,255),3)
        img = cv2_img_add_text(img, text, (x, y2), text_rgb_color=(0, 0, 0),
                               text_size=32)
        #img = cv2.putText(img, f'{conf:2.2f}', (x, y2), font, 1, (0,0,0),3)
    return img
