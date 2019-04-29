# videocr

Extract hardcoded subtitles from videos using the [Tesseract](https://github.com/tesseract-ocr/tesseract) OCR engine with Python.

Input video with hardcoded subtitles:

<p float="left">
  <img width="430" alt="screenshot" src="https://user-images.githubusercontent.com/10210967/56873658-3b76dd00-6a34-11e9-95c6-cd6edc721f58.png">
  <img width="430" alt="screenshot" src="https://user-images.githubusercontent.com/10210967/56873659-3b76dd00-6a34-11e9-97aa-2c3e96fe3a97.png">
</p>

```python
import videocr

print(videocr.get_subtitles('video.avi', lang='HanS'))
```

Output:

``` 
0
00:00:00,000 --> 00:00:02,711
-谢谢 … 你 好 -谢谢
Thank you...Hi. Thanks.

1
00:00:02,794 --> 00:00:04,879
喝 点 什么 ?
What can I get you?

2
00:00:05,046  --> 00:00:12,554
休闲 时 光 …
For relaxing times, make it...

3
00:00:12,804 --> 00:00:14,723
三 得 利 时 光
Bartender, Bob Suntory time.

4
00:00:16,474 --> 00:00:19,144
Un, I'll have a vodka tonic.

5
00:00:19,394 --> 00:00:20,687
谢谢
Laughs Thanks.

```

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

  Language of the subtitles in the video. Besides `eng` for English, all language codes on [this page](https://github.com/tesseract-ocr/tessdata_best/tree/master/script) are supported.

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
