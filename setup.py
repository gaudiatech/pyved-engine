from distutils.core import setup
import os


lib_folder = os.path.dirname(os.path.realpath(__file__))

requirements_file = lib_folder + '/requirements.txt'
whats_required = [] # Here we'll get content of requirements.txt
if os.path.isfile(requirements_file):
    with open(requirements_file) as fp:
        whats_required = fp.read().splitlines()

# need sys so we can include katagames_engine
import sys
sys.path.append('src')
from katagames_engine.__version__ import ENGI_VERSION

from setuptools import setup

pck_list=[
    "katagames_engine",
    "katagames_engine.foundation",
    "katagames_engine.compo",
    "katagames_engine.core",
    "katagames_engine.looparts",  # to be sure we get looparts/rogue.py, looparts/tabletop.py, etc.
    "katagames_engine.looparts.ai",
    "katagames_engine.looparts.demolib",
    "katagames_engine.looparts.gui",
    "katagames_engine.looparts.isometric",
    "katagames_engine.looparts.polarbear",
    "katagames_engine.looparts.tmx",
    "katagames_engine.looparts.tmx.pytiled_parser",
    "katagames_engine.looparts.tmx.pytiled_parser.parsers",
    "katagames_engine.looparts.tmx.pytiled_parser.parsers.json",
    "katagames_engine.looparts.tmx.pytiled_parser.parsers.tmx",
]

setup(
    name='kengi',
    version=str(ENGI_VERSION),
    description='A game engine built on python/pygame',
    keywords=['Python', 'Pygame', 'Game Engine'],
    author='moonb3ndr et al.',
    author_email='thomas.iw@kata.games',
    license='LGPL3',
    package_dir={'': 'src'},
    packages=pck_list,
    url="https://github.com/gaudiatech/kengi",
    install_requires=whats_required,
    include_package_data=True
)
