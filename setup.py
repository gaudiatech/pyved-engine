from distutils.core import setup

import sys
sys.path.append('src')

from katagames_engine.__version__ import ENGI_VERSION

setup(
    name="kengi",
    author="wkta-tom et alii",
    author_email="contact@kata.games",
    url="https://github.com/gaudiatech/kengi",
    package_dir={'': 'src'},
    packages=[
        "katagames_engine",
        "katagames_engine.foundation",
        "katagames_engine.ifaces",
        "katagames_engine.looparts.ai",
        "katagames_engine.looparts.demolib",
        "katagames_engine.looparts.gui",
        "katagames_engine.looparts.isometric",
        "katagames_engine.looparts.polarbear",
        "katagames_engine.looparts.tmx"
        ],
    include_package_data=True,  # to be sure we get _sm_shelf/legacy.py, etc.

    description='pythonic game engine built on top of pygame',
    license='LGPL3',
    version=str(ENGI_VERSION),
)
