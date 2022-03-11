from distutils.core import setup

from katagames_engine.__version__ import ENGI_VERSION

setup(
    name="kengi",
    author="wkta-tom et alii",
    author_email="contact@kata.games",
    url="https://github.com/gaudiatech/kengi",
    packages=["katagames_engine"],
    description='pythonic game engine built on top of pygame',
    license='LGPL3',
    version=str(ENGI_VERSION),
)
