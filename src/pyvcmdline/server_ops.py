import json
import os
import sys

import pyperclip
import requests


# - Config
API_FACADE_URL_TEMPL = 'https://cms{}.kata.games/content/plugins/facade'
API_HOST_PLAY_DEV = 'http://127.0.0.1:8000'
API_SERVICES_URL_TEMPL = "https://services{}.kata.games/pvp"  # could be tweaked via the session file, later on
FRUIT_URL_TEMPLATE_BETA = '{}/play/{}'
FRUIT_URL_TEMPLATE_DEV = "{}/play/{}"  # to add: host, slug
VMSTORAGE_URL = 'https://pyvm.kata.games'
VM_URL_TEMPLATE = 'https://pyvm{}.kata.games'


template_pyconnector_config_file = """
{
  "api_url": "https://services-beta.kata.games",
  "jwt": "ce60ff8ecbeec9d16d7b329be193894d89982abab75bcb02",
  "username": "badmojo",
  "user_id": 6
}
"""


def fetch_remote_game_genres():
    url = get_game_genres_url(False)  # TODO support <dev> and <testnet> modes
    r = requests.get(url)
    li_game_genres = json.loads(r.text)
    return li_game_genres


def get_upload_url(is_dev_mode):
    global VM_URL_TEMPLATE
    # later on
    # full_vm_url = VM_URL_TEMPLATE.format('-beta' if is_dev_mode else '')
    if is_dev_mode:
        full_vm_url = 'http://127.0.0.1:8001'
    else:
        full_vm_url = VM_URL_TEMPLATE.format('')
    # API_HOST_PUSH_DEV = 'http://127.0.0.1:8001'
    # API_ENDPOINT_DEV = '{}/do_upload.php'.format(API_HOST_PUSH_DEV)  # to push a prototype to remote host
    return full_vm_url + '/do_upload.php'


def get_game_genres_url(is_dev_mode):
    global VM_URL_TEMPLATE
    if is_dev_mode:
        raise NotImplementedError
    full_vm_url = VM_URL_TEMPLATE.format('')
    return full_vm_url + '/info_game_classif.php?mode=read'


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
            'application/zip'
            #{'Expires': '0'}
        )
    }
    api_endpoint = get_upload_url(debugmode)
    print('before requests.post')
    reply = requests.post(
        url=api_endpoint,
        files=files,
        timeout=8,  # 8 sec is the max
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
        fruit_url = FRUIT_URL_TEMPLATE_BETA.format(VMSTORAGE_URL, rep_obj[1])
    pyperclip.copy(fruit_url)
    print(f'{fruit_url} has been saved to the paperclip')
