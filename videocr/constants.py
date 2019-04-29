import pathlib

TESSDATA_DIR = pathlib.Path.home() / 'tessdata'

TESSDATA_URL = 'https://github.com/tesseract-ocr/tessdata_fast/raw/master/{}.traineddata'

TESSDATA_SCRIPT_URL = 'https://github.com/tesseract-ocr/tessdata_best/raw/master/script/{}.traineddata'
