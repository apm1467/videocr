from setuptools import setup

with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()

setup(
    name='videocr',
    packages=['videocr'],
    version='0.1.6',
    license='MIT',
    description='Extract hardcoded subtitles from videos using machine learning',
    long_description_content_type='text/markdown',
    long_description=readme,
    author='Yi Ge',
    author_email='me@yige.ch',
    url='https://github.com/apm1467/videocr',
    download_url='https://github.com/apm1467/videocr/archive/v0.1.6.tar.gz',
    install_requires=[
        'rapidfuzz>=0.2.1',
        'opencv-python>=4.1,<5.0',
        'pytesseract>=0.2.6'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
)
