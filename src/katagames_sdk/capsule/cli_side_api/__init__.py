import json

import katagames_sdk.capsule.engine_ground.conf_eng as cgmconf
from katagames_sdk.capsule.networking.httpserver import HttpServer


def get_credentials():
    """
    if pre_auth is True, this function returns info we can extract from session
    :returns: a pair of type (str, int)
    """
    if not cgmconf.runs_in_web():
        raise NotImplementedError

    from browser.session_storage import storage as stor
    return stor['username'], int(stor['playerid'])


def get_user_balance(user_id):
    serv = HttpServer.instance()
    target = serv.get_gtm_app_url() + 'maj_solde.php'
    params = {
        'id_perso': user_id,
        'updating': 0
    }
    res = serv.proxied_get(target, params)
    tmp = json.loads(res)
    if tmp is None:
        raise Exception("Can't retrieve player's balance!")
    else:
        return int(tmp)


def has_pre_auth():
    """
    checks wether we can have username & playerid from session or no,
    [!] it's important that this func works even in non-web ctx
    """
    if not cgmconf.runs_in_web():
        return False
    else:
        print('running katapi.has_preauth...')
        from browser.session_storage import storage as stor
        return ('username' in stor) and ('playerid' in stor)


def save_to_local_session(username, playerid):
    if not cgmconf.runs_in_web():
        raise NotImplementedError
    dict_ref = {
        'username': username,
        'playerid': playerid
    }
    from browser.session_storage import storage as stor
    for key, val in dict_ref.items():
        stor[key] = str(val)


def clear_local_session():
    if not cgmconf.runs_in_web():
        raise NotImplementedError
    from browser.session_storage import storage as stor
    stor.clear()
