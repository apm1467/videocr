from urllib.request import urlopen
import shutil

from . import constants
from .video import Video


def get_subtitles(
        video_path: str, lang='eng', time_start='0:00', time_end='',
        conf_threshold=65, sim_threshold=90, use_fullframe=False) -> str:
    # download tesseract data file to ~/tessdata if necessary
    fpath = constants.TESSDATA_DIR / '{}.traineddata'.format(lang)
    if not fpath.is_file():
        if lang == 'eng':
            url = constants.ENG_URL
        else:
            url = constants.TESSDATA_URL.format(lang)
        constants.TESSDATA_DIR.mkdir(parents=True, exist_ok=True)
        with urlopen(url) as res, open(fpath, 'w+b') as f:
            shutil.copyfileobj(res, f)

    v = Video(video_path)
    v.run_ocr(lang, time_start, time_end, conf_threshold, use_fullframe)
    return v.get_subtitles(sim_threshold)


def save_subtitles_to_file(
        video_path: str, file_path='subtitle.srt', lang='eng',
        time_start='0:00', time_end='', conf_threshold=65, sim_threshold=90,
        use_fullframe=False) -> None:
    with open(file_path, 'w+') as f:
        f.write(get_subtitles(
            video_path, lang, time_start, time_end, conf_threshold,
            sim_threshold, use_fullframe))
