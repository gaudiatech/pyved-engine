import json
from json import JSONDecodeError

from ..capsule.networking.httpserver import HttpServer
from ..engine.foundation import conf_eng as cgmconf
from ..engine import runs_in_web


# from katagames_sdk.capsule.cli_side_api import clear_local_session
# from katagames_sdk.capsule.cli_side_api import has_pre_auth, get_credentials, get_user_balance, save_to_local_session
# from katagames_sdk.capsule.networking.httpserver import HttpServer
# print(has_pre_auth, get_credentials, get_user_balance, save_to_local_session, clear_local_session)

_curr_game_id = 0
_devmode = True

# TODO improve this part
GAME_COSTS = {  # this should be taken from serv side, and forced to avoid hacking
    5: 10,
    6: 10,
    7: 10,
    8: 10,
    9: 10,
    10: 10,
    11: 10
}


class GameNotFound(Exception):
    pass


class GameNotSet(Exception):
    pass


def get_challengeprice():
    global _curr_game_id, GAME_COSTS  # TODO improve, get price thru server
    if _curr_game_id:
        return GAME_COSTS[_curr_game_id]
    else:
        raise GameNotSet


def set_curr_game_id(id_val: int):
    global _curr_game_id
    _curr_game_id = id_val


def get_game_id():
    global _curr_game_id
    if _curr_game_id is None:
        raise GameNotSet
    else:
        return _curr_game_id


def try_auth_server(givenname, plain_pwd):
    """
    :returns:  either id_perso:int >0 , if login is success
    or just False if there was a problem
    """

    uname = givenname

    serv = HttpServer.instance()
    target = serv.get_gtm_app_url() + 'do_auth.php?webmode=0'
    dico_params = {
        'username': uname,
        'password': plain_pwd
    }

    res = serv.proxied_post(target, dico_params)
    print('resultat login---')
    print(res)
    tmp = json.loads(res)

    if tmp:
        res_correct = tmp[0]
        print(res_correct)
        id_perso = tmp[1]
        print(id_perso)
        assert id_perso != 0
        return id_perso
    return False

    # exec. ici => login raté
    # target = serv.get_gtm_app_url() + 'maj_solde.php'
    # params = {
    #     'id_perso': glvars.id_perso,
    #     'updating': 0
    # }
    # res = serv.proxied_get(target, params)
    # tmp = json.loads(res)
    # if tmp is None:
    #     print('WARNING: cannot retrieve players balance!')
    #     return False
    # solde_gp = int(tmp)


def push_score(id_perso: int, avatar_name: str, chall_id: int, score: int) -> bool:
    """
    return True if the prev player's own highscore has been beaten
    """
    global _devmode

    print('~GET READY TO SAVE SCORE~')

    # envoir vers le SERVEUR
    serv = HttpServer.instance()
    url = serv.get_ludo_app_url() + 'tournois.php'

    params = {
        'fct': 'pushscore',
        'game_id': get_game_id(),
        'id_perso': str(id_perso),
        'name': avatar_name,
        'cid': str(chall_id),
        'score': str(score)
    }

    res = serv.proxied_get(url, params)
    if _devmode:
        print('pushed score to server -> Done!')
        print('res= ' + str(res))
        print('msg length is:')
        print(len(res))

    return json.loads(res)  # we expect this server func to return True or False


def pay_for_challenge(given_perso_id):
    """
    :return: bool, int, int
    to say wether the procedure was a success or not

    if it was a success we add 2 values:
      numero_challenge, challenge_seed
    """

    global _curr_game_id

    if _curr_game_id is None:
        raise ValueError('game id has not been set so far!')

    serv = HttpServer.instance()

    # - on récupère n° seed et de tournoi
    target = serv.get_ludo_app_url() + 'tournois.php'
    params = {
        'fct': 'play_it',
        'game_id': str(_curr_game_id)  # identifie le jeu ds le système du ludo.store
    }
    res = serv.proxied_get(target, params)

    try:
        a, b = json.loads(res)
        numero_challenge = int(a)
        chall_seed = int(b)

        # - on paye le droit d'entrée et c'est parti
        params = {
            'fct': 'pay_due',
            'price': str(GAME_COSTS[_curr_game_id]),
            'id_perso': str(given_perso_id),
            'cid': str(numero_challenge)
        }
        res = serv.proxied_get(target, params)
        payment_feedback = json.loads(res)

        return payment_feedback, numero_challenge, chall_seed

    except JSONDecodeError:
        print('ERR** cant decode json')
    except ValueError:
        print('ERR** cant convert to int')
    except KeyError:
        print('ERR** tmp is not a pair of values!')

    raise GameNotFound


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
    if not runs_in_web():
        return False
    else:
        print('running katapi.has_preauth...')
        from browser.session_storage import storage as stor
        return ('username' in stor) and ('playerid' in stor)


def save_to_local_session(username, playerid):
    if not runs_in_web():
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
