"""
    pyved_engine/__main__

    Here, we define the command line interface
    :copyright: Copyright 2018-2024 by the Kata.Games team.
    :license: LGPL-3.0, see LICENSE for details.
"""
import argparse
import importlib
import json
import os
import shutil
import sys
import tempfile  # so we can use a temporary file storage
import time
import zipfile
from pprint import pprint

import pyperclip
import requests  # used to implement the `pyv-cli share` feature

from pyved_engine import vars
from . import pyvcli_config
from .cmdline_utils import do_bundle_renaming, safe_open_question, \
    template_pyconnector_config_file, safe_YN_question, read_metadata, rewrite_metadata, verify_metadata, \
    fetch_remote_game_genres
from .cmdline_utils import is_valid_game_identifier
from .const import *
from .json_prec import TEMPL_ID_TO_JSON_STR
from .pyvcli_cogs import LAUNCH_GAME_SCRIPT_BASENAME
from .pyvcli_cogs import create_folder_and_serialize_dict, recursive_copy
from .pyvcli_cogs import test_isfile_in_cartridge, proc_autogen_localctx, copy_launcher_script
from .pyvcli_config import API_HOST_PLAY_DEV, FRUIT_URL_TEMPLATE_DEV, FRUIT_URL_TEMPLATE_BETA
from .pyvcli_config import VMSTORAGE_URL, API_FACADE_URL_TEMPL, API_SERVICES_URL_TEMPL

__version__ = vars.ENGINE_VERSION_STR


# -----------------------------------
#  kept only to have some 'template' for arg parsing, not using anything below
# -----------------------------------
# from pygments import __version__, highlight
# from pygments.util import ClassNotFound, OptionError, docstring_headline, \
#     guess_decode, guess_decode_from_terminal, terminal_encoding, \
#     UnclosingTextIOWrapper
# from pygments.lexers import get_all_lexers, get_lexer_by_name, guess_lexer, \
#     load_lexer_from_file, get_lexer_for_filename, find_lexer_class_for_filename
# from pygments.lexers.special import TextLexer
# from pygments.formatters.latex import LatexEmbeddedLexer, LatexFormatter
# from pygments.formatters import get_all_formatters, get_formatter_by_name, \
#     load_formatter_from_file, get_formatter_for_filename, find_formatter_class
# from pygments.formatters.terminal import TerminalFormatter
# from pygments.formatters.terminal256 import Terminal256Formatter, TerminalTrueColorFormatter
# from pygments.filters import get_all_filters, find_filter_class
# from pygments.styles import get_all_styles, get_style_by_name

# def _parse_options(o_strs):
#     opts = {}
#     if not o_strs:
#         return opts
#     for o_str in o_strs:
#         if not o_str.strip():
#             continue
#         o_args = o_str.split(',')
#         for o_arg in o_args:
#             o_arg = o_arg.strip()
#             try:
#                 o_key, o_val = o_arg.split('=', 1)
#                 o_key = o_key.strip()
#                 o_val = o_val.strip()
#             except ValueError:
#                 opts[o_arg] = True
#             else:
#                 opts[o_key] = o_val
#     return opts
#
# def _parse_filters(f_strs):
#     filters = []
#     if not f_strs:
#         return filters
#     for f_str in f_strs:
#         if ':' in f_str:
#             fname, fopts = f_str.split(':', 1)
#             filters.append((fname, _parse_options([fopts])))
#         else:
#             filters.append((f_str, {}))
#     return filters
#
# def _print_help(what, name):
#     try:
#         if what == 'lexer':
#             cls = get_lexer_by_name(name)
#             print("Help on the %s lexer:" % cls.name)
#             print(dedent(cls.__doc__))
#         elif what == 'formatter':
#             cls = find_formatter_class(name)
#             print("Help on the %s formatter:" % cls.name)
#             print(dedent(cls.__doc__))
#         elif what == 'filter':
#             cls = find_filter_class(name)
#             print("Help on the %s filter:" % name)
#             print(dedent(cls.__doc__))
#         return 0
#     except (AttributeError, ValueError):
#         print("%s not found!" % what, file=sys.stderr)
#         return 1
#
# def _print_list(what):
#     if what == 'lexer':
#         print()
#         print("Lexers:")
#         print("~~~~~~~")
#
#         info = []
#         for fullname, names, exts, _ in get_all_lexers():
#             tup = (', '.join(names) + ':', fullname,
#                    exts and '(filenames ' + ', '.join(exts) + ')' or '')
#             info.append(tup)
#         info.sort()
#         for i in info:
#             print(('* %s\n    %s %s') % i)
#
#     elif what == 'formatter':
#         print()
#         print("Formatters:")
#         print("~~~~~~~~~~~")
#
#         info = []
#         for cls in get_all_formatters():
#             doc = docstring_headline(cls)
#             tup = (', '.join(cls.aliases) + ':', doc, cls.filenames and
#                    '(filenames ' + ', '.join(cls.filenames) + ')' or '')
#             info.append(tup)
#         info.sort()
#         for i in info:
#             print(('* %s\n    %s %s') % i)
#
#     elif what == 'filter':
#         print()
#         print("Filters:")
#         print("~~~~~~~~")
#
#         for name in get_all_filters():
#             cls = find_filter_class(name)
#             print("* " + name + ':')
#             print("    %s" % docstring_headline(cls))
#
#     elif what == 'style':
#         print()
#         print("Styles:")
#         print("~~~~~~~")
#
#         for name in get_all_styles():
#             cls = get_style_by_name(name)
#             print("* " + name + ':')
#             print("    %s" % docstring_headline(cls))
#
# def _print_list_as_json(requested_items):
#     import json
#     result = {}
#     if 'lexer' in requested_items:
#         info = {}
#         for fullname, names, filenames, mimetypes in get_all_lexers():
#             info[fullname] = {
#                 'aliases': names,
#                 'filenames': filenames,
#                 'mimetypes': mimetypes
#             }
#         result['lexers'] = info
#
#     if 'formatter' in requested_items:
#         info = {}
#         for cls in get_all_formatters():
#             doc = docstring_headline(cls)
#             info[cls.name] = {
#                 'aliases': cls.aliases,
#                 'filenames': cls.filenames,
#                 'doc': doc
#             }
#         result['formatters'] = info
#
#     if 'filter' in requested_items:
#         info = {}
#         for name in get_all_filters():
#             cls = find_filter_class(name)
#             info[name] = {
#                 'doc': docstring_headline(cls)
#             }
#         result['filters'] = info
#
#     if 'style' in requested_items:
#         info = {}
#         for name in get_all_styles():
#             cls = get_style_by_name(name)
#             info[name] = {
#                 'doc': docstring_headline(cls)
#             }
#         result['styles'] = info
#
#     json.dump(result, sys.stdout)

def do_login_via_terminal(ref_metadat, prod_mode=False):
    target_session_config_file = os.path.join(ref_metadat['slug'], 'pyconnector_config.json')
    # read then update...
    # the format is probably like:
    # {
    #     "api_url": "https://services-beta.kata.games/pvp",
    #     "jwt": "d0a14c7dc320584df85cf2eb4a244df6995455b0b5ae54cb",
    #     "username": "Mickeys38",
    #     "user_id": 1
    # }
    print('That cartridge uses ktg_services...')
    empty_session_signature = {
        "api_url": API_SERVICES_URL_TEMPL.format('' if prod_mode else '-beta'),
        "jwt": None,
        "username": None,
        "user_id": None
    }

    print('You can auth, or play as a guest. The choice is yours ***')
    if not os.path.exists(target_session_config_file):  # if no file, we HAVE TO create one now
        with open(target_session_config_file, 'w') as newfile_ptr:
            json.dump(empty_session_signature, newfile_ptr)

    with open(target_session_config_file, 'r') as json_fptr:
        obj = json.load(json_fptr)
        print('session config file read ok->', obj)

    PROMPT_MSG = 'Using pre-defined session stored in {} ; hit N to start a new one. [Y]/N? '
    PROMPT_MSG = PROMPT_MSG.format(target_session_config_file)
    rez = input(PROMPT_MSG)
    while rez not in ('Y', 'N', 'y', 'n', ''):
        print(' invalid reply, please retry:')
        rez = input(PROMPT_MSG)

    if rez in ('y', 'Y', ''):
        return

    PROMPT_MSG = 'Start game as guest? Otherwise you\'ll be prompted to input credentials. [Y]/N? '
    rez = input(PROMPT_MSG)
    while rez not in ('Y', 'N', 'y', 'n', ''):
        print(' invalid reply, please retry:')
        rez = input(PROMPT_MSG)

    if rez in ('y', 'Y', ''):
        # force the guest mode
        obj.update(empty_session_signature)
    else:
        # effective network comms for triggering the auth procedure!
        # special (uncommon) API endpoint:
        # cms-beta.kata.games/content/plugins/facade/user/auth
        # And args are: username, password
        tmp = input('name and pwd, separated by a comma?').split(',')
        while len(tmp) != 2:
            print('unexpected length for the pair username,password. Please re-try')
            tmp = input('name and pwd, separated by a comma?').split(',')
        inp_name, inp_pwd = tmp

        myjson = {'username': inp_name, 'password': inp_pwd}
        adhoc_url = API_FACADE_URL_TEMPL.format('' if prod_mode else '-beta')+'/user/auth'
        req = requests.post(
            adhoc_url,
            data=myjson
        )

        # The expected response is:
        # {"reply_code":200,"message":"","user_id":1,"jwt":"2bed4997e655a9fbfc6f58d03e14747bb375a372a9cd412f"}
        if req.status_code != 200:
            print(adhoc_url)
            raise requests.ConnectionError('cannot auth via the usual API (target component:facade)')
        reply_obj = json.loads(req.text)
        if reply_obj['reply_code'] != 200:
            y = reply_obj['reply_code']
            print('ERROR=:', reply_obj['message'])
            print('-' * 44)
            print()
            raise requests.ConnectionError(f'API for auth can be reached, but bad reply_code noticed: {y}')

        received_jwt = reply_obj['jwt']
        print('Access Granted!')
        obj['jwt'] = received_jwt
        obj['username'] = inp_name
        obj['user_id'] = reply_obj['user_id']

    # persist the session
    with open(target_session_config_file, 'w') as json_fptr:
        json_fptr.write(json.dumps(obj))


def gen_build_date_now():
    return time.ctime(time.time())


def save_list_of_py_files(directory, metadat_obj):
    """
    Recursively find *.py files récursivement tous les fichiers avec une extension .py dans un dossier donné.
    """
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                # Ajoute le chemin relatif à partir du dossier de base
                python_files.append(
                    os.path.relpath(os.path.join(root, file), directory).replace('\\', '/')
                )

    # Mise à jour de la clé "source_files"
    metadat_obj['source_files'] = python_files

    # Update date de construction
    metadat_obj['build_date'] = gen_build_date_now()


def refresh_subcommand(bundle_name):
    print('list of source files has been updated')
    my_metadat = read_metadata(bundle_name)
    save_list_of_py_files(os.path.join(bundle_name, 'cartridge'), my_metadat)
    rewrite_metadata(bundle_name, my_metadat)


def bump_subcommand(bundle_name):
    """
    Nota Bene: operations bump, share automatically update the list of source files
    """
    print('bump bundle to current version that is', __version__)
    my_metadat = read_metadata(bundle_name)
    my_metadat['vmlib_ver'] = __version__.replace('.', '_')
    rewrite_metadata(bundle_name, my_metadat)


def play_subcommand(x, devflag_on):
    if '.' != x and os.path.isdir('cartridge'):
        raise ValueError('launching with a "cartridge" in the current folder, but no parameter "." is forbidden')

    try:
        with open(os.path.join(x, 'cartridge', 'metadat.json'), 'r') as fptr:
            print(f"game bundle {x} found. Reading metadata...")
            metadata = json.load(fptr)

        # - debug
        # print('Metadata:\n', metadata)

        # when ktg_services are enabled, we probably wish to set a user session (=login)
        # this will help:
        if metadata['ktg_services']:
            do_login_via_terminal(metadata, not devflag_on)

        sys.path.append(os.getcwd())
        if x == '.':
            vmsl = importlib.import_module(LAUNCH_GAME_SCRIPT_BASENAME, None)
        else:
            vmsl = importlib.import_module('.' + LAUNCH_GAME_SCRIPT_BASENAME, x)
        vmsl.bootgame(metadata)

    except FileNotFoundError:
        print(f'Error: cannot find the game bundle you specified: {x}')
        print('  Are you sure it exists in the current folder? Alternatively you can try to')
        print('  change directory (cd) and simply type `pyv-cli play`')
        print('  once you are inside the bundle')


def procedure_select_game_genre(mutable_obj):
    """
    @param mutable_obj: metadata to be changed, or no
    """
    prompt0 = 'do yo want to select other genres? Y/[N]'
    prompt1 = 'please select the ones that suit you game,separate by commas:'

    print('it is important to give hints about your game genre. The default genre is')
    if len(mutable_obj['game_genre']) > 1:
        print(','.join(mutable_obj['game_genre']))
    else:
        print(mutable_obj['game_genre'][0])
    inp = input(prompt0)
    while inp not in ('y', 'Y', 'n', 'N', ''):
        print('invalid answer! Re-trying')
        inp = input(prompt0)
    if inp in ('n', 'N', ''):
        return
    # select different genres +failsafe input
    omega = fetch_remote_game_genres()
    print('server currently accepts these values:', omega)
    print(prompt1)

    is_valid_input = False
    new_genres_list = list()
    while not is_valid_input:
        is_valid_input = True
        inp_g = input()
        all_values = inp_g.split(',')
        for k in range(len(all_values)):
            all_values[k] = all_values[k].lstrip()  # remove spaces char. after the comma, if any
        for elt in all_values:
            if elt not in omega:
                is_valid_input = False
                print('error detected in your input, try again. Example of valid input-> "Experimental,Cards"')
                break
        if is_valid_input:
            new_genres_list.extend(all_values)
    mutable_obj['game_genre'] = new_genres_list


def init_command(game_identifier) -> None:
    """
    this is the pyv-cli INIT command, it should create a new game bundle, fully operational
    :param game_identifier: name for your new bundle...
    """
    print(f" Calling sub-command INIT: with game identifier(slug)={game_identifier}")
    print()

    print('  Game templates:')
    for code, name in POSSIB_TEMPLATES.items():
        print(f'    {code}:  {name}')
    template_id = input('select a template: ')
    while not (template_id.isnumeric() and 0 <= int(template_id) <= MAX_TEMPLATE_ID):
        print('invalid input!')
        template_id = input('select a template: ')
    template_id = int(template_id)
    print('-' * 60)

    adhoc_json_prec = TEMPL_ID_TO_JSON_STR[template_id]
    metadata = json.loads(adhoc_json_prec)

    # TODO: shall we use HERE
    #  the network to test if the name is remotely available?
    #  that feature is already implemented by the 'test' subcommand

    while not is_valid_game_identifier(game_identifier):
        print('*** WARNING: the selected game identifier is rejected. Expected format:')
        print(' solely alphanumeric that is A-Z and a-z, plus 0-9 numbers and the underscore _ special character')
        game_identifier = input('enter another game identifier(slug): ')

    x = game_identifier

    metadata['slug'] = x
    tmp = input('whats the name of the game? [Default: Equal to the bundle name]')
    metadata['game_title'] = tmp if len(tmp) > 0 else x

    tmp = input('whos the author? [Default: Unknown]')
    metadata['author'] = tmp if len(tmp) > 0 else 'Unknown'
    metadata['vmlib_ver'] = __version__.replace('.', '_')
    metadata['build_date'] = gen_build_date_now()

    # here, we modify the metadata based on what game genres the user wish to set
    procedure_select_game_genre(metadata)

    # Get the absolute path of the current script
    script_directory = os.path.dirname(os.path.abspath(__file__))
    template_blueprint_folder = os.path.join(script_directory, f'template_{template_id}')
    target_folder = os.path.join(os.getcwd(), x)
    recursive_copy(template_blueprint_folder, target_folder)

    copy_launcher_script(x)
    create_folder_and_serialize_dict(target_folder, data_dict=metadata)
    for _ in range(3):
        print()

    print('GAME BUNDLE=', x)
    print('Important remark: do not rename the name of the folder! (Game bundle)')

    print(f'--->Succesfully created! Now you can type `pyv-cli play {x}`')
    print('Go ahead and have fun ;)')


# import os
# import urllib2
#
#
# class EnhancedFile(file):
#     def __init__(self, *args, **keyws):
#         file.__init__(self, *args, **keyws)
#
#     def __len__(self):
#         return int(os.fstat(self.fileno())[6])


def trigger_publish(slug):
    """
    once the game is available server-side, as a stored cartridge,
    (therefore your game has a slug/Server-side game identifier)

    we trigger the "PUBLISH" op server-side.
    This means the game will spawn/pop within the gaming CMS (cloudarcade)

    :param slug: str that the server uses to uniquely identify a cartridge
    stored server-side
    :return: True/False
    """
    raise NotImplementedError  # deprecated function

    dummy_json_str = """
{
"game_title": "This is the game title",
"slug": "flappy",
"description": "This is a test game",
"instructions": "Click any object to move",
"width": 960,
"height": 720,
"thumb_1": "https://img.gamemonetize.com/ulol31p2l8xogmlxh1yqfa64dxzkyrix/512x384.jpg",
"thumb_2": "https://img.gamemonetize.com/ulol31p2l8xogmlxh1yqfa64dxzkyrix/512x384.jpg",
"category": "Puzzle,Arcade,Action",
"source": "API",
}
"""
    jsondata = json.loads(dummy_json_str)
    jsondata['slug'] = x = slug
    reply = requests.post(
        url='https://kata.games/api/uploads.php',
        data=json.dumps(jsondata)
    )
    print(f'trigger_publish CALLED (arg:x=={x})--- result is...')
    print(reply.text)


# TODO will be useful for implementing a future "repair" bundle subcommand
# def _bundle_renaming(path_to_bundle):
#     # ensure that OUR NORM is respected:
#     # what norm? We need to enforce the rule that states:
#     # the directory name == the slug
#     pass


def _query_slug_availability(x):
    # ---------------------------------------
    #  test for slug availability!
    # ---------------------------------------
    CAN_UPLOAD_SCRIPT = 'can_upload.php'
    slug_avail_serv_truth = requests.get(
        VMSTORAGE_URL + '/' + CAN_UPLOAD_SCRIPT,
        {'slug': x}
    )
    # error handling after ping the VMstorage remote service
    if slug_avail_serv_truth.status_code != 200:
        raise Exception('[netw error] cannot reach the VMstorage service! Contact developers to report that bug please')
    obj_serv_truth = slug_avail_serv_truth.json()
    if ('success' not in obj_serv_truth) or not obj_serv_truth['success']:
        raise Exception('[protocol error] unexpected result after communication with VMstorage service. Contact devs')
    return obj_serv_truth


def ensure_correct_slug(givenslug):
    """
    goal=
    renaming bundle if and only if it is required
    """
    server_truth = _query_slug_availability(givenslug)
    assert (server_truth['success'])
    print('That slug is available' if server_truth['available'] else 'Slug already taken!')
    bval = server_truth['available']

    if not bval:
        print('SUGGESTIONS:')
        for k, elt in enumerate(server_truth['suggestions']):
            print(f'{k}/  {elt}')
        return False, server_truth['suggestions']
    return True, None


def test_subcommand(bundle_name):
    print(f"...Now testing the game bundle title: {bundle_name}")
    metadat = read_metadata(bundle_name)
    err_message = verify_metadata(metadat)

    if err_message is None:
        # ensure that thumbnails & assets described do exist:
        print('ensuring if assets exist')
        files_exp_li = [  # all expected files need to be known
            metadat['thumbnail512x384'],
            metadat['thumbnail512x512']
        ]
        for asset_name in metadat['asset_list']:
            files_exp_li.append(metadat['asset_base_folder']+'/'+asset_name)

        for elt in files_exp_li:
            print('____testing file:', elt)
            if not test_isfile_in_cartridge(elt, bundle_name):
                raise FileNotFoundError('cannot find asset:', elt)
        print('assets --->OK')
        print()

        print('COHESION test:', bundle_name == metadat['slug'])
        print()

        print('~ Serv-side Slug Availability? ~')
        obj = _query_slug_availability(metadat['slug'])
        if not obj['success']:
            raise ValueError('cannot read info from server!')
        print(' ->', 'yes' if obj['available'] else 'no')
        if not obj['available']:
            print('suggestions:')
            pprint(obj['suggestions'])
    else:  # metadat is not valid
        raise ValueError('Invalid metadata file! ' + err_message)


def upload_my_zip_file(zip_file_path: str, gslug, debugmode: bool) -> None:
    """
    :zip_file_path: as param name indicates
    :param: dev_mode is a flag to say if we target the dev server or prod server...
    Side effect: puts something important in the paperclip!
    """
    # ----------------------
    #  test if paperclip can indeed, be accessed
    # ----------------------
    try:
        pyperclip.copy('hello world')
    except pyperclip.PyperclipException:
        info_err_url = 'https://pyperclip.readthedocs.io/en/latest/#not-implemented-error'
        print('FATAL ERROR! A required software component was not found on your system.')
        print('In order to enable the pyved-engine \'s usage of the paperclip')
        print('you MUST first use a command such as:')
        print()
        print('   sudo apt-get install xclip')
        print()
        print('This will upgrade components available on your systems.')
        print(f'For more information, please refer to: {info_err_url}')
        print('If the command does not solve your problem, get in touch with KataGames devs via Discord')
        sys.exit(16)

    # ----------------------
    #  push file to the server
    # ----------------------
    if zip_file_path[-3:] != 'zip':  # to ensure we dont forget the extension:
        raise ValueError('the argument `zip_file_path` is expected to use the extension .zip')
    files = {
        'uploadedFile': (
            zip_file_path,
            open(zip_file_path, 'rb'),
            'application/zip',
            {'Expires': '0'}
        )
    }
    api_endpoint = pyvcli_config.get_upload_url(debugmode)
    reply = requests.post(
        url=api_endpoint,
        files=files,
        data={'pyv-cli-flag': True, 'chosen-slug': gslug, 'uploadBtn': 'Upload'}
    )
    try:
        rep_obj = json.loads(reply.text)
    except json.decoder.JSONDecodeError:
        print('cannot parse server response!')
        print('raw text was:')
        print(reply.text)
        sys.exit(15)
    print('server responde to request:\n', rep_obj[0])

    # ------------------------
    #  save target URL to the paperclip
    # -----------------------
    if debugmode:
        fruit_url = FRUIT_URL_TEMPLATE_DEV.format(API_HOST_PLAY_DEV, rep_obj[1])
    else:
        fruit_url = FRUIT_URL_TEMPLATE_BETA.format(pyvcli_config.VMSTORAGE_URL, rep_obj[1])
    pyperclip.copy(fruit_url)
    print(f'{fruit_url} has been saved to the paperclip')


def pack_game_cartridge(bundl_name, using_temp_dir=True) -> str:
    """
    @param bundl_name:
    @param using_temp_dir:
    @return: a path to the produced ZIP archive
    """
    wrapper_bundle = os.path.join(os.getcwd(), bundl_name)
    zip_precise_target = os.path.join(wrapper_bundle, 'cartridge')

    def _inner_func(source_folder, wanted_zip_filename='output.zip'):
        systmp_directory = tempfile.gettempdir()
        output_zip_path = os.path.join(systmp_directory, wanted_zip_filename)
        with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(source_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_folder)
                    zipf.write(file_path, arcname)
        return output_zip_path

    return _inner_func(zip_precise_target)


def share_subcommand(bundle_name, dev_flag_on):
    # TODO in the future,
    #  we may want to create a 'pack' subcommand that would only produce the .zip, not send it elsewhere
    # that pack subcommand would pack and send it to the cwd, whereas the classic pack uses the tempfile/tempdir logic

    # - refresh list of files
    metadat = read_metadata(bundle_name)
    save_list_of_py_files(os.path.join(bundle_name, 'cartridge'), metadat)
    rewrite_metadata(bundle_name, metadat)

    slug = metadat['slug']
    if dev_flag_on:  # in devmode, all tests on metadata are skipped
        zipfile_path = pack_game_cartridge(slug)
        upload_my_zip_file(zipfile_path, slug, True)
        return

    err_msg_lines = [
        'ERROR: the "share" is impossible yet, invalid metadat.json detected.',
        'Please use "pyv-cli test BundleName"',
        'in order to get more information and fix the problem'
    ]
    # if we're in prod mode, we HAVE TO pass all tests (slug is valid & available, etc.)
    # before uploading
    if verify_metadata(metadat) is None:
        slug_correctness = ensure_correct_slug(slug)
        while not slug_correctness[0]:
            tmp = input('what alternative do you choose (please select a number: 0 to 3)? ')
            if not (tmp.isnumeric() and (-1 < int(tmp) < 4)):
                print('invalid input, please retry.')
            else:
                choice = int(tmp)
                slug = slug_correctness[1][choice]
                slug_correctness = ensure_correct_slug(slug)
                # when renaming, both the metadata and the folder name need to be changed
                do_bundle_renaming(bundle_name, slug)
                bundle_name = slug
        zipfile_path = pack_game_cartridge(bundle_name)
        upload_my_zip_file(zipfile_path, slug, False)
    else:
        for msg_line in err_msg_lines:  # printing a multi-line error message
            print(msg_line)


def upgrade_subcmd(bundlename):
    """
    ordre dans lequel l'algo procèdera, idéalement:
    [1] rebuild le py_connecteur L (local ctx) à la volée, à partir du fichier de SPEC trouvé
    [2] update des metadata
    [3] constitution d'un module network avec ledit connecteur renommé en __init__.py,
    [4] insertion code network vers le chemin bundle/network
    [5] écrasement launch_game.py par la version moddée
    """

    # TODO:
    # faut fix ce souci
    #
    # a l'heure actuelle, le fichier de API spec n'est PAS utilisé pour générer dynamiquement le pyconnector Local
    # on utilise ce qu'il y a dans pyvcmdline/spare_parts

    # étape 1 préparatifs
    obj = read_metadata(bundlename)
    bundle_location = os.path.join(os.getcwd(), bundlename)
    netw_dir = os.path.join(bundle_location, 'network')
    if obj['ktg_services']:
        print('***WARNING*** ktg_services is already set to true!')
        rez = safe_YN_question('Do you wish to keep existing files, not rewriting the pyConnector config?', 'y')
        if rez == 'y':
            print('Upgrade operation aborted!')
            return
        else:
            if os.path.isdir(netw_dir):
                shutil.rmtree(netw_dir)

    # ÉTAPE 2: Génération pyConnector, ou prise en compte "spare_parts/network.py"
    # pour le déplacer dans bundle_folder/network
    using_autogen = safe_YN_question('Do you prefer to use the static pyConnector (no autogen)?', 'y')
    if using_autogen == 'y':
        root_pyvcli = os.path.dirname(os.path.abspath(__file__))
        read_from_netw = os.path.join(root_pyvcli, 'spare_parts', 'network.py')
        target_file = os.path.join(bundle_location, 'network', '__init__.py')
    else:
        print('cant use the autogen, its not implemented just yet')
        raise NotImplementedError

    # TODO améliorations, avec autogen
    # etape 3, création du dossier network dans le bundle folder
    # Pas implem comme il faudrait (là on récupère un network.py statique)
    bundle_location = os.path.join(os.getcwd(), bundlename)
    new_dir = os.path.join(bundle_location, 'network')
    if os.path.isdir(new_dir):
        raise Exception('folder "network" exists in bundle, but non-consistent metadata found')
    os.makedirs(new_dir)

    # étape 4 stricto sensu
    shutil.copy(read_from_netw, target_file)
    obj['ktg_services'] = True
    rewrite_metadata(bundlename, obj)

    # etape 5:
    pyconnector_config_obj = json.loads(template_pyconnector_config_file)
    new_url = safe_open_question('whats the URL for api services?', pyconnector_config_obj['api_url'])
    new_jwt = safe_open_question('jwt value?', None)
    new_user_id = safe_open_question('user_id?', None)
    new_username = safe_open_question('username?', None)
    pyconnector_config_obj['api_url'] = new_url
    pyconnector_config_obj['jwt'] = new_jwt
    pyconnector_config_obj['user_id'] = new_user_id
    pyconnector_config_obj['username'] = new_username
    path_written_config = os.path.join(bundle_location, 'pyconnector_config.json')
    with open(path_written_config, 'w') as fptr:
        fptr.write(json.dumps(pyconnector_config_obj))
        print('file:', path_written_config, 'has been written')

    # etape 6: impacter launch_game.py
    copy_launcher_script(bundlename, False)


def _remove_junk_from_bundle_name(x):
    """
    if a trailing slash or backslash
     is found, then we need to remove it
    """
    t = x.rstrip('/')
    t = t.rstrip('\\')
    return t


def main_inner(parser, argns):
    # definitions
    subcommand_mapping = {
        'init': init_command,
        'test': test_subcommand,
        'upgrade': upgrade_subcmd,
        'play': play_subcommand,
        'share': share_subcommand,
        'pub': None,
        'bump': bump_subcommand,
        'refresh': refresh_subcommand,
        'autogen': proc_autogen_localctx
    }
    no_arg_subcommands = {'autogen'}
    extra_flags_subcommands = {'share', 'play'}  # mark all subcommands that use the 'dev' mode flag

    # the algorithm
    ope_name = argns.subcommand

    if argns.version:
        print(VERSION_PRINT_MESSAGE % __version__)
        return 0
    if argns.help:
        parser.print_help()
        return 0
    if ope_name not in subcommand_mapping:
        parser.print_help()
        return 1
    if subcommand_mapping[ope_name] is None:
        raise NotImplementedError(f"subcommand \"{ope_name}\" is valid, but isnt implemented yet!")

    adhoc_subcommand_func = subcommand_mapping[ope_name]
    if ope_name in no_arg_subcommands:
        # a few subcommands do not take an argument
        adhoc_subcommand_func()
    else:
        xarg = _remove_junk_from_bundle_name(argns.bundle_name)
        if ope_name not in extra_flags_subcommands:
            adhoc_subcommand_func(xarg)
        else:
            # a few subcommands require the the dev mode flag!
            adhoc_subcommand_func(xarg, argns.dev)
    return 0

    # handle ``pygmentize -L``
    # if argns.L is not None:
    #     arg_set = set()
    #     for k, v in vars(argns).items():
    #         if v:
    #             arg_set.add(k)
    #
    #     arg_set.discard('L')
    #     arg_set.discard('json')
    #
    #     if arg_set:
    #         parser.print_help(sys.stderr)
    #         return 2
    #
    #     # print version
    #     if not argns.json:
    #         main(['', '-V'])
    #     allowed_types = {'lexer', 'formatter', 'filter', 'style'}
    #     largs = [arg.rstrip('s') for arg in argns.L]
    #     if any(arg not in allowed_types for arg in largs):
    #         parser.print_help(sys.stderr)
    #         return 0
    #     if not largs:
    #         largs = allowed_types
    #     if not argns.json:
    #         for arg in largs:
    #             _print_list(arg)
    #     else:
    #         _print_list_as_json(largs)
    #     return 0
    #
    # # handle ``pygmentize -H``
    # if argns.H:
    #     if not is_only_option('H'):
    #         parser.print_help(sys.stderr)
    #         return 2
    #     what, name = argns.H
    #     if what not in ('lexer', 'formatter', 'filter'):
    #         parser.print_help(sys.stderr)
    #         return 2
    #     return _print_help(what, name)
    #
    # # parse -O options
    # parsed_opts = _parse_options(argns.O or [])
    #
    # # parse -P options
    # for p_opt in argns.P or []:
    #     try:
    #         name, value = p_opt.split('=', 1)
    #     except ValueError:
    #         parsed_opts[p_opt] = True
    #     else:
    #         parsed_opts[name] = value
    #
    # # encodings
    # inencoding = parsed_opts.get('inencoding', parsed_opts.get('encoding'))
    # outencoding = parsed_opts.get('outencoding', parsed_opts.get('encoding'))
    #
    # # handle ``pygmentize -N``
    # if argns.N:
    #     lexer = find_lexer_class_for_filename(argns.N)
    #     if lexer is None:
    #         lexer = TextLexer
    #
    #     print(lexer.aliases[0])
    #     return 0
    #
    # # handle ``pygmentize -C``
    # if argns.C:
    #     inp = sys.stdin.buffer.read()
    #     try:
    #         lexer = guess_lexer(inp, inencoding=inencoding)
    #     except ClassNotFound:
    #         lexer = TextLexer
    #
    #     print(lexer.aliases[0])
    #     return 0
    #
    # # handle ``pygmentize -S``
    # S_opt = argns.S
    # a_opt = argns.a
    # if S_opt is not None:
    #     f_opt = argns.f
    #     if not f_opt:
    #         parser.print_help(sys.stderr)
    #         return 2
    #     if argns.l or argns.INPUTFILE:
    #         parser.print_help(sys.stderr)
    #         return 2
    #
    #     try:
    #         parsed_opts['style'] = S_opt
    #         fmter = get_formatter_by_name(f_opt, **parsed_opts)
    #     except ClassNotFound as err:
    #         print(err, file=sys.stderr)
    #         return 1
    #
    #     print(fmter.get_style_defs(a_opt or ''))
    #     return 0
    #
    # # if no -S is given, -a is not allowed
    # if argns.a is not None:
    #     parser.print_help(sys.stderr)
    #     return 2
    #
    # # parse -F options
    # F_opts = _parse_filters(argns.F or [])
    #
    # # -x: allow custom (eXternal) lexers and formatters
    # allow_custom_lexer_formatter = bool(argns.x)
    #
    # # select lexer
    # lexer = None
    #
    # # given by name?
    # lexername = argns.l
    # if lexername:
    #     # custom lexer, located relative to user's cwd
    #     if allow_custom_lexer_formatter and '.py' in lexername:
    #         try:
    #             filename = None
    #             name = None
    #             if ':' in lexername:
    #                 filename, name = lexername.rsplit(':', 1)
    #
    #                 if '.py' in name:
    #                     # This can happen on Windows: If the lexername is
    #                     # C:\lexer.py -- return to normal load path in that case
    #                     name = None
    #
    #             if filename and name:
    #                 lexer = load_lexer_from_file(filename, name,
    #                                              **parsed_opts)
    #             else:
    #                 lexer = load_lexer_from_file(lexername, **parsed_opts)
    #         except ClassNotFound as err:
    #             print('Error:', err, file=sys.stderr)
    #             return 1
    #     else:
    #         try:
    #             lexer = get_lexer_by_name(lexername, **parsed_opts)
    #         except (OptionError, ClassNotFound) as err:
    #             print('Error:', err, file=sys.stderr)
    #             return 1
    #
    # # read input code
    # code = None
    #
    # if argns.INPUTFILE:
    #     if argns.s:
    #         print('Error: -s option not usable when input file specified',
    #               file=sys.stderr)
    #         return 2
    #
    #     infn = argns.INPUTFILE
    #     try:
    #         with open(infn, 'rb') as infp:
    #             code = infp.read()
    #     except Exception as err:
    #         print('Error: cannot read infile:', err, file=sys.stderr)
    #         return 1
    #     if not inencoding:
    #         code, inencoding = guess_decode(code)
    #
    #     # do we have to guess the lexer?
    #     if not lexer:
    #         try:
    #             lexer = get_lexer_for_filename(infn, code, **parsed_opts)
    #         except ClassNotFound as err:
    #             if argns.g:
    #                 try:
    #                     lexer = guess_lexer(code, **parsed_opts)
    #                 except ClassNotFound:
    #                     lexer = TextLexer(**parsed_opts)
    #             else:
    #                 print('Error:', err, file=sys.stderr)
    #                 return 1
    #         except OptionError as err:
    #             print('Error:', err, file=sys.stderr)
    #             return 1
    #
    # elif not argns.s:  # treat stdin as full file (-s support is later)
    #     # read code from terminal, always in binary mode since we want to
    #     # decode ourselves and be tolerant with it
    #     code = sys.stdin.buffer.read()  # use .buffer to get a binary stream
    #     if not inencoding:
    #         code, inencoding = guess_decode_from_terminal(code, sys.stdin)
    #         # else the lexer will do the decoding
    #     if not lexer:
    #         try:
    #             lexer = guess_lexer(code, **parsed_opts)
    #         except ClassNotFound:
    #             lexer = TextLexer(**parsed_opts)
    #
    # else:  # -s option needs a lexer with -l
    #     if not lexer:
    #         print('Error: when using -s a lexer has to be selected with -l',
    #               file=sys.stderr)
    #         return 2
    #
    # # process filters
    # for fname, fopts in F_opts:
    #     try:
    #         lexer.add_filter(fname, **fopts)
    #     except ClassNotFound as err:
    #         print('Error:', err, file=sys.stderr)
    #         return 1
    #
    # # select formatter
    # outfn = argns.o
    # fmter = argns.f
    # if fmter:
    #     # custom formatter, located relative to user's cwd
    #     if allow_custom_lexer_formatter and '.py' in fmter:
    #         try:
    #             filename = None
    #             name = None
    #             if ':' in fmter:
    #                 # Same logic as above for custom lexer
    #                 filename, name = fmter.rsplit(':', 1)
    #
    #                 if '.py' in name:
    #                     name = None
    #
    #             if filename and name:
    #                 fmter = load_formatter_from_file(filename, name,
    #                                                  **parsed_opts)
    #             else:
    #                 fmter = load_formatter_from_file(fmter, **parsed_opts)
    #         except ClassNotFound as err:
    #             print('Error:', err, file=sys.stderr)
    #             return 1
    #     else:
    #         try:
    #             fmter = get_formatter_by_name(fmter, **parsed_opts)
    #         except (OptionError, ClassNotFound) as err:
    #             print('Error:', err, file=sys.stderr)
    #             return 1
    #
    # if outfn:
    #     if not fmter:
    #         try:
    #             fmter = get_formatter_for_filename(outfn, **parsed_opts)
    #         except (OptionError, ClassNotFound) as err:
    #             print('Error:', err, file=sys.stderr)
    #             return 1
    #     try:
    #         outfile = open(outfn, 'wb')
    #     except Exception as err:
    #         print('Error: cannot open outfile:', err, file=sys.stderr)
    #         return 1
    # else:
    #     if not fmter:
    #         if os.environ.get('COLORTERM', '') in ('truecolor', '24bit'):
    #             fmter = TerminalTrueColorFormatter(**parsed_opts)
    #         elif '256' in os.environ.get('TERM', ''):
    #             fmter = Terminal256Formatter(**parsed_opts)
    #         else:
    #             fmter = TerminalFormatter(**parsed_opts)
    #     outfile = sys.stdout.buffer
    #
    # # determine output encoding if not explicitly selected
    # if not outencoding:
    #     if outfn:
    #         # output file? use lexer encoding for now (can still be None)
    #         fmter.encoding = inencoding
    #     else:
    #         # else use terminal encoding
    #         fmter.encoding = terminal_encoding(sys.stdout)
    #
    # # provide coloring under Windows, if possible
    # if not outfn and sys.platform in ('win32', 'cygwin') and \
    #         fmter.name in ('Terminal', 'Terminal256'):  # pragma: no cover
    #     # unfortunately colorama doesn't support binary streams on Py3
    #     outfile = UnclosingTextIOWrapper(outfile, encoding=fmter.encoding)
    #     fmter.encoding = None
    #     try:
    #         import colorama.initialise
    #     except ImportError:
    #         pass
    #     else:
    #         outfile = colorama.initialise.wrap_stream(
    #             outfile, convert=None, strip=None, autoreset=False, wrap=True)
    #
    # # When using the LaTeX formatter and the option `escapeinside` is
    # # specified, we need a special lexer which collects escaped text
    # # before running the chosen language lexer.
    # escapeinside = parsed_opts.get('escapeinside', '')
    # if len(escapeinside) == 2 and isinstance(fmter, LatexFormatter):
    #     left = escapeinside[0]
    #     right = escapeinside[1]
    #     lexer = LatexEmbeddedLexer(left, right, lexer)
    #
    # # ... and do it!
    # if not argns.s:
    #     # process whole input as per normal...
    #     try:
    #         highlight(code, lexer, fmter, outfile)
    #     finally:
    #         if outfn:
    #             outfile.close()
    #     return 0
    # else:
    #     # line by line processing of stdin (eg: for 'tail -f')...
    #     try:
    #         while 1:
    #             line = sys.stdin.buffer.readline()
    #             if not line:
    #                 break
    #             if not inencoding:
    #                 line = guess_decode_from_terminal(line, sys.stdin)[0]
    #             highlight(line, lexer, fmter, outfile)
    #             if hasattr(outfile, 'flush'):
    #                 outfile.flush()
    #         return 0
    #     except KeyboardInterrupt:  # pragma: no cover
    #         return 0
    #     finally:
    #         if outfn:
    #             outfile.close()


# class HelpFormatter(argparse.HelpFormatter):
#     def __init__(self, prog, indent_increment=2, max_help_position=16, width=None):
#         if width is None:
#             try:
#                 width = shutil.get_terminal_size().columns - 2
#             except Exception:
#                 pass
#         argparse.HelpFormatter.__init__(self, prog, indent_increment,
#                                         max_help_position, width)


def do_parse_args():
    """
    Main command line entry point.
    """
    script_desc = "Command line tool for pyved-engine, used to operate with/manipulate game bundles."
    # parser = argparse.ArgumentParser(description=desc, add_help=False,
    #                                  formatter_class=HelpFormatter)
    parser = argparse.ArgumentParser(
        description=script_desc,
        add_help=False,
        usage="pyv-cli [option] subcommand [subcommand_options]"
    )

    # ----------------
    #  extras
    # ----------------
    special_modes_group = parser.add_argument_group(
        'Options')

    either_one_option = special_modes_group.add_mutually_exclusive_group()
    either_one_option.add_argument(
        '-v', '--version', action='store_true',
        help='Print the current pyved engine version.')
    either_one_option.add_argument(
        '-h', '--help', action='store_true',
        help='Print this help.')
    either_one_option.add_argument(
        '-d', '--dev', action='store_true',
        help='Use the developer server (tool debug etc)'
    )

    # Declare all subcommands
    subparsers = parser.add_subparsers(title="Subcommands", dest="subcommand", required=False)

    # ——————————————————————————————————
    # +++ INIT subcommand
    init_parser = subparsers.add_parser("init", help="used to initialize a new game bundle")
    init_parser.add_argument("bundle_name", type=str, help="Name of the bundle")

    # ——————————————————————————————————
    # +++ PLAY subcommand
    play_parser = subparsers.add_parser(
        "play", help="play a given game bundle in the local context"
    )
    play_parser.add_argument(
        "bundle_name", type=str, nargs="?", default=".", help="Specified bundle (default: current folder)"
    )

    # ——————————————————————————————————
    # +++ AUTOGEN subcommand
    autogen = subparsers.add_parser(
        "autogen", help="for system devs only (=a dev tool equivalent to a PyConnector autogen script)"
    )

    # ——————————————————————————————————
    # +++ UPGRADE subcommand:
    # the goal here is to enable katagames API calls from inside a game
    play_parser = subparsers.add_parser(
        "upgrade", help="Upgrade a given game, to enable katagames API calls"
    )
    play_parser.add_argument(
        "bundle_name", type=str, help="Specified bundle"
    )

    # ——————————————————————————————————
    # +++ TEST subcommand
    play_parser = subparsers.add_parser(
        "test", help="can be used to test if the specified game bundle is valid or not"
    )
    play_parser.add_argument(
        "bundle_name", type=str
    )
    # ——————————————————————————————————
    # +++ REFRESH subcommand
    play_parser = subparsers.add_parser(
        "refresh", help="refreshes the list of all source-files, and modify the bundle metadata accordingly"
    )
    play_parser.add_argument(
        "bundle_name", type=str
    )
    # ——————————————————————————————————
    # +++ BUMP subcommand
    play_parser = subparsers.add_parser(
        "bump", help="can be used to upgrade the metadata, to mark that we use the current pyved-engine revision"
    )
    play_parser.add_argument(
        "bundle_name", type=str
    )

    # ——————————————————————————————————
    # +++ SHARE subcommand {
    share_parser = subparsers.add_parser(
        "share", help="Share a given game bundle with the world"
    )
    share_parser.add_argument(
        "bundle_name", type=str, nargs="?", default=".", help="Specified bundle (default: current folder)"
    )

    # ——————————————————————————————————
    # +++ PUB subcommand {
    pubpp = subparsers.add_parser(
        "pub", help="request game publication given a game slug share via the sandboxed mode"
    )
    pubpp.add_argument(
        "slug", type=str, help="existing game slug (=identifier in the cloud-based storage)"
    )

    ret_args = parser.parse_args()
    # print('debug:')
    # print(ret_args)
    # print()
    main_inner(parser, ret_args)

    # flags_only = parser.add_argument_group('Flags')
    # flags_only.add_argument(
    #     '-v', action='store_true',
    #     help='Print out engine version information'
    # )

    # operation = parser.add_argument_group('Main operation')
    # lexersel = operation.add_mutually_exclusive_group()
    # lexersel.add_argument(
    #     '-l', metavar='LEXER',
    #     help='Specify the lexer to use.  (Query names with -L.)  If not '
    #          'given and -g is not present, the lexer is guessed from the filename.')
    # lexersel.add_argument(
    #     '-g', action='store_true',
    #     help='Guess the lexer from the file contents, or pass through '
    #          'as plain text if nothing can be guessed.')
    # operation.add_argument(
    #     '-F', metavar='FILTER[:options]', action='append',
    #     help='Add a filter to the token stream.  (Query names with -L.) '
    #          'Filter options are given after a colon if necessary.')
    # operation.add_argument(
    #     '-f', metavar='FORMATTER',
    #     help='Specify the formatter to use.  (Query names with -L.) '
    #          'If not given, the formatter is guessed from the output filename, '
    #          'and defaults to the terminal formatter if the output is to the '
    #          'terminal or an unknown file extension.')
    # operation.add_argument(
    #     '-O', metavar='OPTION=value[,OPTION=value,...]', action='append',
    #     help='Give options to the lexer and formatter as a comma-separated '
    #          'list of key-value pairs. '
    #          'Example: `-O bg=light,python=cool`.')
    # operation.add_argument(
    #     '-P', metavar='OPTION=value', action='append',
    #     help='Give a single option to the lexer and formatter - with this '
    #          'you can pass options whose value contains commas and equal signs. '
    #          'Example: `-P "heading=Pygments, the Python highlighter"`.')
    # operation.add_argument(
    #     '-o', metavar='OUTPUTFILE',
    #     help='Where to write the output.  Defaults to standard output.')
    #
    # operation.add_argument(
    #     'INPUTFILE', nargs='?',
    #     help='Where to read the input.  Defaults to standard input.')
    #
    # flags = parser.add_argument_group('Operation flags')
    # flags.add_argument(
    #     '-v', action='store_true',
    #     help='Print a detailed traceback on unhandled exceptions, which '
    #          'is useful for debugging and bug reports.')
    # flags.add_argument(
    #     '-s', action='store_true',
    #     help='Process lines one at a time until EOF, rather than waiting to '
    #          'process the entire file.  This only works for stdin, only for lexers '
    #          'with no line-spanning constructs, and is intended for streaming '
    #          'input such as you get from `tail -f`. '
    #          'Example usage: `tail -f sql.log | pygmentize -s -l sql`.')
    # flags.add_argument(
    #     '-x', action='store_true',
    #     help='Allow custom lexers and formatters to be loaded from a .py file '
    #          'relative to the current working directory. For example, '
    #          '`-l ./customlexer.py -x`. By default, this option expects a file '
    #          'with a class named CustomLexer or CustomFormatter; you can also '
    #          'specify your own class name with a colon (`-l ./lexer.py:MyLexer`). '
    #          'Users should be very careful not to use this option with untrusted '
    #          'files, because it will import and run them.')
    # flags.add_argument('--json', help='Output as JSON. This can '
    #                                   'be only used in conjunction with -L.',
    #                    default=False,
    #                    action='store_true')
    #
    # special_modes_group = parser.add_argument_group(
    #     'Special modes - do not do any highlighting')

    # special_modes = special_modes_group.add_mutually_exclusive_group()
    # special_modes.add_argument(
    #     '-S', metavar='STYLE -f formatter',
    #     help='Print style definitions for STYLE for a formatter '
    #          'given with -f. The argument given by -a is formatter '
    #          'dependent.')
    # special_modes.add_argument(
    #     '-L', nargs='*', metavar='WHAT',
    #     help='List lexers, formatters, styles or filters -- '
    #          'give additional arguments for the thing(s) you want to list '
    #          '(e.g. "styles"), or omit them to list everything.')
    # special_modes.add_argument(
    #     '-N', metavar='FILENAME',
    #     help='Guess and print out a lexer name based solely on the given '
    #          'filename. Does not take input or highlight anything. If no specific '
    #          'lexer can be determined, "text" is printed.')
    # special_modes.add_argument(
    #     '-C', action='store_true',
    #     help='Like -N, but print out a lexer name based solely on '
    #          'a given content from standard input.')
    # special_modes.add_argument(
    #     '-H', action='store', nargs=2, metavar=('NAME', 'TYPE'),
    #     help='Print detailed help for the object <name> of type <type>, '
    #          'where <type> is one of "lexer", "formatter" or "filter".')
    # special_modes.add_argument(
    #     '-V', action='store_true',
    #     help='Print the package version.')
    # special_modes.add_argument(
    #     '-h', '--help', action='store_true',
    #     help='Print this help.')
    # special_modes_group.add_argument(
    #     '-a', metavar='ARG',
    #     help='Formatter-specific additional argument for the -S (print '
    #          'style sheet) mode.')

    # argns = parser.parse_args(args[1:])
    # try:
    #     return main_inner(parser, argns)
    # except BrokenPipeError:
    #     # someone closed our stdout, e.g. by quitting a pager.
    #     return 0
    # except Exception:
    #     if argns.v:
    #         print(file=sys.stderr)
    #         print('*' * 65, file=sys.stderr)
    #         print('An unhandled exception occurred while highlighting.',
    #               file=sys.stderr)
    #         print('Please report the whole traceback to the issue tracker at',
    #               file=sys.stderr)
    #         print('<https://github.com/pygments/pygments/issues>.',
    #               file=sys.stderr)
    #         print('*' * 65, file=sys.stderr)
    #         print(file=sys.stderr)
    #         raise
    #     import traceback
    #     info = traceback.format_exception(*sys.exc_info())
    #     msg = info[-1].strip()
    #     if len(info) >= 3:
    #         # extract relevant file and position info
    #         msg += '\n   (f%s)' % info[-2].split('\n')[0].strip()[1:]
    #     print(file=sys.stderr)
    #     print('*** Error while highlighting:', file=sys.stderr)
    #     print(msg, file=sys.stderr)
    #     print('*** If this is a bug you want to report, please rerun with -v.',
    #           file=sys.stderr)
    #     return 1


if __name__ == '__main__':  # to allow to run the current file via "python3 -m pyvcmdline"
    do_parse_args()
