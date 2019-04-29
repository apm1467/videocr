from distutils.core import setup

setup(
    name = 'videocr',
    packages = ['videocr'],
    version = '0.1.1',
    license = 'MIT',
    description = 'Extract hardcoded subtitles from videos using machine learning',
    author = 'Yi Ge',
    author_email = 'me@yige.ch',
    url = 'https://github.com/apm1467/videocr',
    download_url = 'https://github.com/apm1467/videocr/archive/v0.1.tar.gz',
    install_requires = [
        'fuzzywuzzy>=0.17',
        'python-Levenshtein>=0.12',
        'opencv-python>=4.1,<5.0',
        'pytesseract>=0.2.6'
    ],
    classifiers = [
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: MIT License',
      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: 3.7',
    ],
)