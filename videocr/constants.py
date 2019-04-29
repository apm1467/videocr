import pathlib

TESSDATA_DIR = pathlib.Path.home() / 'tessdata'

ENG_URL = 'https://github.com/tesseract-ocr/tessdata_fast/raw/master/eng.traineddata'

TESSDATA_URL = 'https://github.com/tesseract-ocr/tessdata_best/raw/master/script/{}.traineddata'
