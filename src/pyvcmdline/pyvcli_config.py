"""
Constants for the sub command "share"
"""


API_HOST_PLAY_DEV = 'http://127.0.0.1:8000'
FRUIT_URL_TEMPLATE_DEV = "{}/play/{}"  # to add: host, slug
VM_URL_TEMPLATE = 'https://pyvm{}.kata.games'
VMSTORAGE_URL = 'https://pyvm.kata.games'
FRUIT_URL_TEMPLATE_BETA = '{}/play/{}'

# contains -beta or not
API_SERVICES_URL_TEMPL = "https://services{}.kata.games/pvp"  # could be tweaked via the session file, later on
API_FACADE_URL_TEMPL = 'https://cms{}.kata.games/content/plugins/facade'


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
