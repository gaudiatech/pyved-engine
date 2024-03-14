"""
Constants for the sub command "share"
"""


API_HOST_PLAY_DEV = 'http://127.0.0.1:8001'

API_HOST_PUSH_DEV = 'http://127.0.0.1:8001'
API_ENDPOINT_DEV = '{}/do_upload.php'.format(API_HOST_PUSH_DEV)  # to push a prototype to remote host
FRUIT_URL_TEMPLATE_DEV = "{}/play/{}"  # to add: host, slug


BETA_VM_API_HOST = 'https://pyvm.kata.games'
VMSTORAGE_URL = 'https://pyvm.kata.games'

API_ENDPOINT_BETA = '{}/do_upload.php'.format(BETA_VM_API_HOST)
FRUIT_URL_TEMPLATE_BETA = '{}/play/{}'
