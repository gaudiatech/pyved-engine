"""
this module contains only misc functions (think of it as utilities),
that are hidden from outside,
and are included in __main__.py only to ease pyv-cli subcommands implementation.

Syntactic sugar:
  from pyvcli_cogs import *
spawns all useful misc functions in the current scope, all at once
"""
import json
import os
import shutil
from .autogen_localctx import proc_autogen_localctx


__all__ = [
    'LAUNCH_GAME_SCRIPT_BASENAME',

    'copy_launcher_script',
    'create_folder_and_serialize_dict',
    'proc_autogen_localctx',
    'read_metadata',
    'recursive_copy',
    'rewrite_metadata',
    'test_isfile_in_cartridge',
    'verify_metadata'
]

# public constants
LAUNCH_GAME_SCRIPT_BASENAME = 'launch_game'

# private constants
BASIC_LAUNCH_GAME_SCRIPT_LOC = ('..', 'spare_parts', 'launch_game0.py')
NETW_LAUNCH_GAME_SCRIPT_LOC = ('..', 'spare_parts', 'launch_game1.py')

# private alias
fpath_join = os.path.join


def copy_launcher_script(bundlename, basic_bundle=True):
    """
    sélectionne le bon script & le copie vers le bundle identifié par bundlename
    """
    # prepare the launch_game.py script
    root_pyvcli = os.path.dirname(os.path.abspath(__file__))
    ylist = BASIC_LAUNCH_GAME_SCRIPT_LOC if basic_bundle else NETW_LAUNCH_GAME_SCRIPT_LOC
    src_file = fpath_join(os.path.join(root_pyvcli, *ylist))

    filename = f"{LAUNCH_GAME_SCRIPT_BASENAME}.py"
    dest_file = fpath_join(os.getcwd(), bundlename, filename)

    # Nota Bene:
    # shutil.copy2 preserves the original metadata, copy doesnt
    # here, i can use copy, as launch_game.py metadata doesnt matter
    shutil.copy(src_file, dest_file)


def create_folder_and_serialize_dict(folder0_name, data_dict):
    # Check if the folder exists, create it if not
    folder1_name = fpath_join(folder0_name, 'cartridge')
    if not os.path.exists(folder1_name):
        os.makedirs(folder1_name)
    # Serialize the dictionary using JSON and create a JSON file
    json_file_path = fpath_join(folder1_name, 'metadat.json')
    with open(json_file_path, 'w') as json_file:
        json.dump(data_dict, json_file, indent=4)


def recursive_copy(source_folder, destination_folder):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    for item in os.listdir(source_folder):
        source_item = fpath_join(source_folder, item)
        destination_item = fpath_join(destination_folder, item)
        if os.path.isdir(source_item):
            recursive_copy(source_item, destination_item)
        else:
            shutil.copy2(source_item, destination_item)


def test_isfile_in_cartridge(filename, bundle_name) -> bool:
    wrapper_folder = fpath_join(os.getcwd(), bundle_name)
    cartridge_folder = fpath_join(wrapper_folder, 'cartridge')
    targ = os.path.sep.join((cartridge_folder, filename))
    return os.path.isfile(targ)
