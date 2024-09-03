import os
import tempfile
import zipfile
import re
import json

template_pyconnector_config_file ="""
{
  "api_url": "https://services-beta.kata.games",
  "jwt": "ce60ff8ecbeec9d16d7b329be193894d89982abab75bcb02",
  "username": "badmojo",
  "user_id": 6
}
"""


def verify_metadata(mdat_obj) -> str:
    """
    confirm that the metadata contains all required fields
    returns a str if something is missing!
    """
    expected_fields = (
        'assets',
        'author',
        'build_date',
        'dependencies',
        'description',
        'title',
        'instructions',
        'slug',
        'sounds',
        'thumbnail512x384',
        'thumbnail512x512',
        'ktg_services',
        'vmlib_ver',
        'uses_challenge',
        'has_game_server'
    )
    for k in expected_fields:
        if k not in mdat_obj:
            return k


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
        fptr.write(json.dumps(blob_obj))


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
