# PY CONNECTOR, automatically gen. Do not modify by hand!
# filename:auto_connector.py - generation date: 2024-03-19 11:55:33
import requests
import json

api_url = 'https://t-api-beta.kata.games'


# ----dummy----, thats not network
def get_jwt():
    return 'abcde'


def get_username():
    return None


def get_user_id():
    return None


class GetResult:
    def __init__(self, rawtxt):
        self.text = rawtxt

    def to_json(self):
        return json.loads(self.text)


def _ensure_type_hexstr(data):
    # Ensure that the provided data is a string containing only hexadecimal characters.
    if isinstance(data, str) and all(c in '0123456789abcdefABCDEF' for c in data):
        return True
    return False


def _get_request(url, given_data=None):
    try:
        response = requests.get(f"{api_url}{url}", params=given_data)
        print('sending GET, url:', f"{api_url}{url}")
        print('sending GET, params:', given_data)
        response.raise_for_status()
        print('raw result:', response.text)
        return GetResult(response.text)
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None


# added alias
def get(url, data=None):
    return _get_request(url, data)


def _post_request(url, given_data=None):
    try:
        print('sending POST, url:', f"{api_url}{url}")
        print('sending POST, params:', given_data)
        response = requests.post(f"{api_url}{url}", json=given_data)
        response.raise_for_status()
        print('raw result:', response.text)
        return GetResult(response.text)
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None


def get_version():
    # GET request to /version
    try:
        resobj = _get_request('/version')
        return resobj.to_json()
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None


def get_user_infos(user_id: int):
    # GET request to /user/infos
    try:
        resobj = _get_request('/user/infos', {'user_id': user_id})
        return resobj.to_json()
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None


def can_pay_challenge(jwt: str, game_id: int):
    # GET request to /challenge/canPay
    if not _ensure_type_hexstr(jwt):
        raise Exception("hexstr type not recognized!, value:", jwt)
    try:
        resobj = _get_request('/challenge/canPay', {'jwt': jwt, 'game_id': game_id})
        return resobj.to_json()
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None


def get_rank(user_id: int, game_id: int):
    # GET request to /challenge/user/rank
    try:
        resobj = _get_request('/challenge/user/rank', {'user_id': user_id, 'game_id': game_id})
        return resobj.to_json()
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None


def can_pay_game_fee(jwt: str, game_price: int):
    # GET request to /games/canPayGameFee
    if not _ensure_type_hexstr(jwt):
        raise Exception("hexstr type not recognized!, value:", jwt)
    try:
        resobj = _get_request('/games/canPayGameFee', {'jwt': jwt, 'game_price': game_price})
        return resobj.to_json()
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None


def pay_challenge(jwt: str, game_id: int):
    # GET request to /challenge/pay
    if not _ensure_type_hexstr(jwt):
        raise Exception("hexstr type not recognized!, value:", jwt)
    try:
        resobj = _get_request('/challenge/pay', {'jwt': jwt, 'game_id': game_id})
        return resobj.to_json()
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None


def register_score(score: int, token: str):
    # GET request to /challenge/score
    if not _ensure_type_hexstr(token):
        raise Exception("hexstr type not recognized!, value:", token)
    try:
        resobj = _get_request('/challenge/score', {'score': score, 'token': token})
        return resobj.to_json()
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None


def pay_game_fee(jwt: str, game_id: int, game_price: int):
    # GET request to /games/payGameFee
    if not _ensure_type_hexstr(jwt):
        raise Exception("hexstr type not recognized!, value:", jwt)
    try:
        resobj = _get_request('/games/payGameFee', {'jwt': jwt, 'game_id': game_id, 'game_price': game_price})
        return resobj.to_json()
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None


def auth(username: str, password: str):
    # GET request to /user/auth
    try:
        resobj = _get_request('/user/auth', {'username': username, 'password': password})
        return resobj.to_json()
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None
