import json
import os
import re

import requests

from . import pyvcli_config


EXP_METADAT_KEYS = (
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

template_pyconnector_config_file ="""
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

    # we also need to test whether Y or N, categories specified are still recognized within the CMS!
    if (not isinstance(mdat_obj['game_genre'], list)) or (len(mdat_obj['game_genre']) == 0):
        return 'Invalid metadat format: value tied to "game_genre" has to be a list with non-zero length'
    ok_game_genres = fetch_remote_game_genres()
    for elt in mdat_obj['game_genre']:
        if elt not in ok_game_genres:
            return f'Game genre "{elt}" rejected by the Kata.Games system, please contact an Admin, or replace value'
    print('--Metadata is valid--')


def read_metadata(bundle_name):
    # Check if the folder exists, otherwise we'll throw an error
    wrapper_bundle = os.path.join(os.getcwd(), bundle_name)
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


def rewrite_metadata(bundle_name, blob_obj):
    wrapper_bundle = os.path.join(os.getcwd(), bundle_name)
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


def is_valid_game_identifier(test_identifier):
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
