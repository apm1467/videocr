import pathlib

TESSDATA_DIR = pathlib.Path.home() / 'tessdata'

TESSDATA_URL = 'https://github.com/tesseract-ocr/tessdata_fast/raw/main/{}.traineddata'

TESSDATA_SCRIPT_URL = 'https://github.com/tesseract-ocr/tessdata_best/raw/main/script/{}.traineddata'
