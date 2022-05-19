from distutils.core import setup

from katagames_engine.__version__ import ENGI_VERSION

setup(
    name="kengi",
    author="wkta-tom et alii",
    author_email="contact@kata.games",
    url="https://github.com/gaudiatech/kengi",
    packages=[
        "katagames_engine",
        "katagames_engine.foundation",
        "katagames_engine._sm_shelf.event",
        "katagames_engine._sm_shelf.gui",
        "katagames_engine._sm_shelf.isometric",
        "katagames_engine._sm_shelf.tmx",
        "katagames_engine._sm_shelf.polarbear"
        ],
    include_package_data=True,  # to be sure we get _sm_shelf/legacy.py, etc.

    description='pythonic game engine built on top of pygame',
    license='LGPL3',
    version=str(ENGI_VERSION),
)
