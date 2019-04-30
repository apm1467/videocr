# videocr

Extract hardcoded (burned-in) subtitles from videos using the [Tesseract](https://github.com/tesseract-ocr/tesseract) OCR engine with Python.

Input a video with hardcoded subtitles:

<p float="left">
  <img width="430" alt="screenshot" src="https://user-images.githubusercontent.com/10210967/56873658-3b76dd00-6a34-11e9-95c6-cd6edc721f58.png">
  <img width="430" alt="screenshot" src="https://user-images.githubusercontent.com/10210967/56873659-3b76dd00-6a34-11e9-97aa-2c3e96fe3a97.png">
</p>

```python
# print_sub.py

import videocr

if __name__ == '__main__':
    print(videocr.get_subtitles('video.avi', lang='chi_sim+eng', sim_threshold=70))
```

`$ python3 print_sub.py`

Output:

``` 
0
00:00:01,042 --> 00:00:02,877
喝 点 什么 ? 
What can I get you?

1
00:00:03,044 --> 00:00:05,463
我 不 知道
Um, I'm not sure.

2
00:00:08,091 --> 00:00:10,635
休闲 时 光 …
For relaxing times, make it...

3
00:00:10,677 --> 00:00:12,595
三 得 利 时 光
Bartender, Bob Suntory time.

4
00:00:14,472 --> 00:00:17,142
我 要 一 杯 伏特 加
Un, I'll have a vodka tonic.

5
00:00:18,059 --> 00:00:19,019
谢谢
Laughs Thanks.
```

## Performance

The OCR process runs in parallel and is CPU intensive. It takes 3 minutes on my dual-core laptop to extract a 20 seconds video. You may want more cores for longer videos.

## Installation

1. Install [Tesseract](https://github.com/tesseract-ocr/tesseract/wiki) and make sure it is in your `$PATH`

2. `$ pip install videocr`

## API

```python
videocr.get_subtitles(
        video_path: str, lang='eng', time_start='0:00', time_end='',
        conf_threshold=65, sim_threshold=90, use_fullframe=False)
```
Return the subtitles string in SRT format.


```python

videocr.save_subtitles_to_file(
        video_path: str, file_path='subtitle.srt', lang='eng', time_start='0:00',
        time_end='', conf_threshold=65, sim_threshold=90, use_fullframe=False)
```
Write subtitles to `file_path`. If the file does not exist, it will be created automatically.

### Parameters

- `lang`

  The language of the subtitles. You can extract subtitles in almost any language. All language codes on [this page](https://github.com/tesseract-ocr/tesseract/wiki/Data-Files#data-files-for-version-400-november-29-2016) (e.g. `'eng'` for English) and all script names in [this repository](https://github.com/tesseract-ocr/tessdata_fast/tree/master/script) (e.g. `'HanS'` for simplified Chinese) are supported.
  
  Note that you can use more than one language. For example, `'hin+eng'` means using Hindi and English together for recognition. More details are available in the [Tesseract documentation](https://github.com/tesseract-ocr/tesseract/wiki/Command-Line-Usage#using-multiple-languages).
  
  Language data files will be automatically downloaded to your `$HOME/tessdata` directory when necessary. You can read more about Tesseract language data files on their [wiki page](https://github.com/tesseract-ocr/tesseract/wiki/Data-Files).

- `time_start` and `time_end`

  Extract subtitles from only a part of the video. The subtitle timestamps are still calculated according to the full video length.

- `conf_threshold`

  Confidence threshold for word predictions. Words with lower confidence than this threshold are discarded. The default value is fine for most cases. 

  Make it closer to 0 if you get too few words from the predictions, or make it closer to 100 if you get too many excess words.

- `sim_threshold`

  Similarity threshold for subtitle lines. Neighbouring subtitles with larger [Levenshtein](https://en.wikipedia.org/wiki/Levenshtein_distance) ratios than this threshold will be merged together. The default value is fine for most cases.

  Make it closer to 0 if you get too many duplicated subtitle lines, or make it closer to 100  if you get too few subtitle lines.

- `use_fullframe`

  By default, only the bottom half of each frame is used for OCR. You can explicitly use the full frame if your subtitles are not within the bottom half of each frame.
