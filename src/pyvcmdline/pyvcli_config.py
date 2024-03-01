

# ---------------------
# constants for the sub command "share"
# ---------------------

API_HOST_PLAY_DEV = 'http://127.0.0.1:8001'

API_HOST_PUSH_DEV = 'http://127.0.0.1:8001'
API_ENDPOINT_DEV = '{}/webapp_backend/do_upload.php'.format(API_HOST_PUSH_DEV)  # to push a prototype to remote host
FRUIT_URL_TEMPLATE_DEV = "{}play/{}"  # to add: host, slug

API_HOST_PLAY_BETA = 'https://beta.kata.games'

API_HOST_PUSH_BETA = 'https://jeuxtomi.alwaysdata.net'
API_ENDPOINT_BETA = '{}/do_upload.php'.format(API_HOST_PUSH_BETA)
FRUIT_URL_TEMPLATE_BETA = '{}/wrapper?slug={}'
