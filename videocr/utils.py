from urllib.request import urlopen
import shutil

from . import constants


# download language data files to ~/tessdata if necessary
def download_lang_data(lang: str):
    constants.TESSDATA_DIR.mkdir(parents=True, exist_ok=True)

    for lang_name in lang.split('+'):
        filepath = constants.TESSDATA_DIR / '{}.traineddata'.format(lang_name)
        if not filepath.is_file():
            # download needed file
            if lang_name[0].isupper():
                url = constants.TESSDATA_SCRIPT_URL.format(lang_name)
            else:
                url = constants.TESSDATA_URL.format(lang_name)

            with urlopen(url) as res, open(filepath, 'w+b') as f:
                shutil.copyfileobj(res, f)
