import json
import os
import re

import requests

from . import pyvcli_config


EXP_METADAT_KEYS = (
    'dependencies',
    'asset_base_folder',
    'asset_list',
    'sound_base_folder',
    'sound_list',

    'vmlib_ver',
    'author',
    'build_date',
    'dependencies',
    'description',
    'title',
    'instructions',
    'slug',
    'thumbnail512x384',
    'thumbnail512x512',
    'ktg_services',
    'source_files',

    'uses_challenge',
    'has_game_server',
    'ncr_faucet',
    'game_genre'
)


class MetadatEntries:
    """
    what you find below should match what has been written above,
    this is used to avoid harmful typos when implementing pyv-cli subcommands...
    and also to set default values in a clean way
    """
    GameTitle = 'title'
    Slug = 'slug'
    Genre = 'game_genre'
    Author = 'author'
    Date = 'build_date'
    Libs = 'dependencies'

    # default values
    DefaultAuthor = 'Unknown'


template_pyconnector_config_file = """
{
  "api_url": "https://services-beta.kata.games",
  "jwt": "ce60ff8ecbeec9d16d7b329be193894d89982abab75bcb02",
  "username": "badmojo",
  "user_id": 6
}
"""


def fetch_remote_game_genres():
    url = pyvcli_config.get_game_genres_url(False)  # TODO support <dev> and <testnet> modes
    r = requests.get(url)
    li_game_genres = json.loads(r.text)
    return li_game_genres


def verify_metadata(mdat_obj) -> str:
    """
    confirm that the metadata contains all required fields
    returns a str if something is missing!
    """
    global EXP_METADAT_KEYS
    for k in EXP_METADAT_KEYS:
        if k not in mdat_obj:
            return 'Missing key= {}'.format(k)
    # need to test that pyved_engine is in dependencies...
    if "pyved_engine" not in mdat_obj['dependencies']:
        return 'Invalid list detected: "pyved_engine" not listed in the list of dependencies'

    # we also need to test whether Y or N, categories specified are still recognized within the CMS!
    if (not isinstance(mdat_obj['game_genre'], list)) or (len(mdat_obj['game_genre']) == 0):
        return 'Invalid metadat format: value tied to "game_genre" has to be a list with non-zero length'
    ok_game_genres = fetch_remote_game_genres()
    for elt in mdat_obj['game_genre']:
        if elt not in ok_game_genres:
            return f'Game genre "{elt}" rejected by the Kata.Games system, please contact an Admin, or replace value'
    print('Metadata->OK')


def read_metadata(bundle_name, specific_dir=None):
    # Check if the folder exists, otherwise we'll throw an error
    if specific_dir is None:
        wrapper_bundle = os.path.join(os.getcwd(), bundle_name)
    else:
        wrapper_bundle = os.path.join(specific_dir, bundle_name)
        print('reading metadat...')
        print('looking in:', wrapper_bundle)

    if not os.path.exists(wrapper_bundle):
        raise FileNotFoundError(f'ERR! Cant find the specified game bundle ({bundle_name})')
    cartridge_folder = os.path.join(wrapper_bundle, 'cartridge')
    if not os.path.exists(cartridge_folder):
        raise ValueError('ERR! Bundle format isnt valid, cartridge structure is missing')

    # need to open cartridge, read metadata,
    whats_open = os.path.sep.join((cartridge_folder, 'metadat.json'))
    # print('READING', whats_open, '...')
    f_ptr = open(whats_open, 'r')
    obj = json.load(f_ptr)
    f_ptr.close()
    return obj


def rewrite_metadata(bundle_name, blob_obj, specific_dir=None):
    if specific_dir is None:
        tdir = os.getcwd()
    else:
        tdir = specific_dir
    wrapper_bundle = os.path.join(tdir, bundle_name)
    cartridge_folder = os.path.join(wrapper_bundle, 'cartridge')
    what_to_open = os.path.sep.join((cartridge_folder, 'metadat.json'))
    print(f'REWRITING file {what_to_open}...')
    with open(what_to_open, 'w') as fptr:
        json.dump(blob_obj, fptr, indent=2)


def do_bundle_renaming(source, dest):
    print('Renaming the game bundle...')
    print(f'{source} --> {dest}')
    if os.path.isdir(dest):
        raise ValueError(f'cannot rename game bundle, because {dest} already exists in the current folder')
    md_obj = read_metadata(source)
    os.rename(source, dest)
    md_obj['slug'] = dest
    rewrite_metadata(dest, md_obj)
    print('OK.')


def has_right_syntax_for_slug(test_identifier):
    ok_pattern = '^[a-zA-Z0-9_]+$'
    return bool(re.match(ok_pattern, test_identifier))


def safe_YN_question(prompt, default_answer):
    full_prompt_msg = f'{prompt} y/n? [Default val={default_answer}]'
    res = input(full_prompt_msg)
    while res not in ('', 'y', 'n', 'Y', 'N'):
        res = input(full_prompt_msg)
    res = res.lower()  # enforce no caps
    if res == '':
        res = default_answer
    return res


def safe_open_question(prompt, default_answer):
    full_prompt_msg = f'{prompt} value? [Default val={default_answer}]'
    res = input(full_prompt_msg)
    if len(res) == 0:
        res = default_answer
    return res
