from distutils.core import setup

import sys
sys.path.append('src')

import os
lib_folder = os.path.dirname(os.path.realpath(__file__))
requirement_path = lib_folder + '/requirements.txt'
install_requires = [] # Here we'll get content of requirements.txt
if os.path.isfile(requirement_path):
    with open(requirement_path) as f:
        install_requires = f.read().splitlines()

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
    install_requires=install_requires,
    description='pythonic game engine built on top of pygame',
    license='LGPL3',
    version=str(ENGI_VERSION),
)
