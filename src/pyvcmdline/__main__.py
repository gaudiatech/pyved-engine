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
import re
import shutil
import sys
import tempfile
import time
import zipfile
from pprint import pprint

import pyperclip
import requests  # used to implement the `pyv-cli share` feature
from .pyvcli_cogs import *
from pyved_engine import vars
from .const import *
from .json_prec import TEMPL_ID_TO_JSON_STR
from .pyvcli_config import API_HOST_PLAY_DEV, API_ENDPOINT_DEV, \
    FRUIT_URL_TEMPLATE_DEV
from .pyvcli_config import BETA_VM_API_HOST, API_ENDPOINT_BETA, FRUIT_URL_TEMPLATE_BETA
from .pyvcli_config import VMSTORAGE_URL

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


def play_subcommand(x):
    if '.' != x and os.path.isdir('cartridge'):
        raise ValueError('launching with a "cartridge" in the current folder, but no parameter "." is forbidden')
    metadata = None
    try:
        fptr = open(os.path.join(x, 'cartridge', 'metadat.json'), 'r')
        metadata = json.load(fptr)
        fptr.close()
        print(f"game bundle {x} found. Loading...")
        print('Metadata:\n', metadata)
    except FileNotFoundError:
        print(f'Error: cannot find the game bundle you specified: {x}')
        print('  Are you sure it exists in the current folder? Alternatively you can try to')
        print('  change directory (cd) and simply type `pyv-cli play`')
        print('  once you are inside the bundle')

    if metadata is not None:
        sys.path.append(os.getcwd())
        if x == '.':
            vmsl = importlib.import_module(LAUNCH_GAME_SCRIPT_BASENAME, None)
        else:
            vmsl = importlib.import_module('.' + LAUNCH_GAME_SCRIPT_BASENAME, x)
        vmsl.bootgame(metadata)


def _is_valid_identifier(test_identifier):
    ok_pattern = '^[a-zA-Z0-9_]+$'
    return bool(re.match(ok_pattern, test_identifier))


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

    while not _is_valid_identifier(game_identifier):
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

    metadata['build_date'] = time.ctime(time.time())

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


def create_zip_from_folder(bundle_name, source_folder):
    # origin_no_sep = source_folder.rstrip('/\\')
    tmp_output_zip_filename = 'output.zip'
    temp_dir = tempfile.gettempdir()
    # print('temp_dir=', temp_dir)
    output_zip_path = os.path.join(temp_dir, tmp_output_zip_filename)
    # print('writing zip file in:', output_zip_filename)
    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(source_folder):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_folder)
                zipf.write(file_path, arcname)

    # move from temp dir to cwd
    source_file = output_zip_path
    destination_file = os.path.join(os.getcwd(), f"{bundle_name}.zip")
    shutil.copy(source_file, destination_file)
    print('Newly created file:', destination_file)
    return destination_file


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
    # check that can be deserialized...
    jsondata = json.loads(dummy_json_str)
    jsondata['slug'] = x = slug
    # jsondata['cartridge'] = y = slug
    # print(jsondata)
    # print(type(jsondata))

    reply = requests.post(
        url=TARG_TRIGGER_PUBLISH,
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

    print('availability?', server_truth['available'])
    if not (server_truth['available']):
        print('SUGGESTIONS:')
        for elt in server_truth['suggestions']:
            print('   *', elt)
    print()
    print('-' * 60)


def test_subcommand(bundle_name):
    print(f"***TESTING bundle {bundle_name}***")

    metadat = read_metadata(bundle_name)
    pprint(metadat)
    print()
    btest = verify_metadata(metadat)
    print('valid metadata?', btest is None)
    if btest is not None:
        raise ValueError('Invalid metadata file! Missing key= {}'.format(btest))

    # ensure that thumbnails & assets described do exist:
    print('ensuring if assets exist')
    files_exp_li = [  # all expected files need to be known
        metadat['thumbnail512x384'],
        metadat['thumbnail512x512']
    ]
    files_exp_li.extend(metadat['assets'])
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


def upload_my_zip_file(zip_file_path: str, gslug, debugmode: bool) -> None:
    """
    :zip_file_path: as param name indicates
    :param: dev_mode is a flag to say if we target the dev server or prod server...

    Side effect: puts something important in the paperclip!
    """
    file_to_send = zip_file_path  # dont forget the extension!
    api_endpoint = API_ENDPOINT_DEV if debugmode else API_ENDPOINT_BETA
    # serv_host = DEV_SERVER_HOST if dev_mode else PROD_SERVER_HOST

    files = {
        'uploadedFile': (file_to_send,
                         open(file_to_send, 'rb'),
                         'application/zip',
                         {'Expires': '0'})
    }
    reply = requests.post(
        url=api_endpoint,
        files=files,
        data={'pyv-cli-flag': True, 'chosen-slug': gslug, 'uploadBtn': 'Upload'}
    )
    print('upload_my_zip_file called! Resp. is:')
    print(reply.text)
    rep_obj = json.loads(reply.text)
    if debugmode:
        fruit_url = FRUIT_URL_TEMPLATE_DEV.format(API_HOST_PLAY_DEV, rep_obj[1])
    else:
        fruit_url = FRUIT_URL_TEMPLATE_BETA.format(BETA_VM_API_HOST, rep_obj[1])

    pyperclip.copy(fruit_url)
    print(f'URL:{fruit_url} has been copied to the paperclip!')

    # new and shiny (ver1 . august23):
    # theFile = EnhancedFile('a.xml', 'r')
    # theUrl = "http://example.com/abcde"
    # theHeaders = {'Content-Type': 'text/xml'}
    # theRequest = urllib2.Request(theUrl, theFile, theHeaders)
    # response = urllib2.urlopen(theRequest)
    # theFile.close()
    # for line in response:
    #     print
    #     line

    # ----- old shit: ------
    # Extract data from the ZIP file
    # with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    #    extracted_data = zip_ref.read(zip_ref.namelist()[0])

    # Prepare the HTTP POST request
    # files = {'zip_data': ('data.zip', extracted_data)}
    # response = requests.post(server_url, files=files)

    # Example usage
    # zip_file_path = "path/to/your/file.zip"
    # server_url = "http://example.com/upload.php"
    # response = upload_zip_file(zip_file_path, server_url)
    # print("Response status code:", response.status_code)
    # print("Response content:", response.text)


def share_subcommand(bundle_name, dev_flag_on):
    # FIRST, need to answer the question: whats the slug name?
    metadata = read_metadata(bundle_name)
    slug = metadata['slug']
    print('slug found:', slug)

    # pre-made func usage
    wrapper_bundle = os.path.join(os.getcwd(), bundle_name)
    zip_precise_target = os.path.join(wrapper_bundle, 'cartridge')

    fn = create_zip_from_folder(bundle_name, zip_precise_target)
    # print("ZIP file created:", output_zip_filename)
    # create_zip_from_folder(, os.getcwd())
    # print('tmpfile created ok')
    upload_my_zip_file(fn, slug, dev_flag_on)


def upgrade_subcmd(bundlename):
    """
    ordre dans lequel l'algo procèdera, idéalement:
    [1] rebuild le py_connecteur L (local ctx) à la volée, à partir du fichier de SPEC trouvé
    [2] update des metadata
    [3] constitution d'un module network avec ledit connecteur renommé en __init__.py,
    [4] insertion code network vers le chemin bundle/network
    [5] écrasement launch_game.py par la version moddée
    """
    # prép. etapes 2 & 3
    obj = read_metadata(bundlename)
    if obj['ktg_services']:
        print('***WARNING*** ktg_services is already set to True.\n'
              + 'In order to avoid unexpected behavior, the bundle isnt upgraded')
        return
    # tests anticipés pr gérer erreurs:
    bundle_location = os.path.join(os.getcwd(), bundlename)
    new_dir = os.path.join(bundle_location, 'network')
    if os.path.isdir(new_dir):
        raise Exception('folder "network" exists in bundle, but non-consistent metadata found')

    # étape 2 stricto sensu
    obj['ktg_services'] = True
    rewrite_metadata(bundlename, obj)

    # TODO améliorations, avec autogen
    # etape 3, quasi-ok. Pas implem comme il faudrait (là on récupère un network.py statique)
    bundle_location = os.path.join(os.getcwd(), bundlename)
    new_dir = os.path.join(bundle_location, 'network')
    if os.path.isdir(new_dir):
        raise Exception('folder "network" exists in bundle, but non-consistent metadata found')
    os.makedirs(new_dir)

    # etape 4: transfert network component
    root_pyvcli = os.path.dirname(os.path.abspath(__file__))
    read_from_netw = os.path.join(root_pyvcli, 'spare_parts', 'network.py')
    target_file = os.path.join(bundle_location, 'network', '__init__.py')
    shutil.copy(read_from_netw, target_file)

    # etape 5: impacter launch_game.py
    copy_launcher_script(bundlename, False)


def main_inner(parser, argns):
    # definitions
    subcommand_mapping = {
        'init': init_command,
        'test': test_subcommand,
        'upgrade': upgrade_subcmd,
        'play': play_subcommand,
        'share': share_subcommand,
        'pub': None,
        'autogen': proc_autogen_localctx
    }
    no_arg_subcommands = {'autogen'}
    extra_flags_subcommands = {'share'}  # mark all subcommands that use the 'dev' mode flag

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
    elif ope_name not in extra_flags_subcommands:
        adhoc_subcommand_func(argns.bundle_name)
    else:
        # a few subcommands require the the dev mode flag!
        adhoc_subcommand_func(argns.bundle_name, argns.dev)
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
    init_parser = subparsers.add_parser("init", help="Initialize something")
    init_parser.add_argument("bundle_name", type=str, help="Name of the bundle")

    # ——————————————————————————————————
    # +++ PLAY subcommand
    play_parser = subparsers.add_parser(
        "play", help="Play a given game bundle now!"
    )
    play_parser.add_argument(
        "bundle_name", type=str, nargs="?", default=".", help="Specified bundle (default: current folder)"
    )

    # ——————————————————————————————————
    # +++ AUTOGEN subcommand
    autogen = subparsers.add_parser(
        "autogen", help="Command to be used only by admins ->tool for py connector autogen"
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
        "test", help="only for debug"
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
        "pub", help="Publish a game based on its slug"
    )
    pubpp.add_argument(
        "slug", type=str, help="Chosen slug (slug = cartridge identifier in the cloud-based game warehouse)"
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
