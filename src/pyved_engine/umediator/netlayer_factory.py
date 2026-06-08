"""
Class to provide high flexibility in network communications.

It allows for easy switching between different interfaces by constructing
the appropriate one on demand. This is achieved by passing two arguments:

- Context: Game with both client and server components
"""
import importlib


__all__ = [
    'build_netlayer',
    'build_netlayer_from_module',
    'register_transport_layer',
    'resolve_transport_code',
    'Objectifier'
]


class Objectifier:
    def __init__(self, **entries):
        self.__dict__.update(entries)


def _normalize_code(name):
    if name is None:
        return None
    return str(name).strip().upper()


_TRANSPORT_LAYER_SPECS = {
    "SOCKET": {
        "client": "netw_socket_cli",
        "server": "netw_socket_server",
    },
    "WS": {
        "client": "netw_ws_client",
        "server": "netw_ws_serv",
    },
    "WEB_SOCKET_RELAY": {
        "client": "netw_ws_client",
        "server": "netw_ws_serv",
    },
    "WEB_COMPAT_WS": {
        "client": "netw_ws_client",
        "server": "netw_ws_serv",
    },
}


def register_transport_layer(code, client_module_name, server_module_name, aliases=None):
    """
    Register a transport layer by symbolic code.

    This keeps the factory open to injected transport implementations from
    other projects, while preserving the built-in socket/websocket backends.
    """
    normalized_code = _normalize_code(code)
    if not normalized_code:
        raise ValueError("transport layer code must be a non-empty string")
    _TRANSPORT_LAYER_SPECS[normalized_code] = {
        "client": client_module_name,
        "server": server_module_name,
    }
    for alias in aliases or ():
        normalized_alias = _normalize_code(alias)
        if normalized_alias:
            _TRANSPORT_LAYER_SPECS[normalized_alias] = _TRANSPORT_LAYER_SPECS[normalized_code]


def resolve_transport_code(param1=None):
    """
    Resolve the symbolic transport code used by the engine.

    Priority order:
    - FORCE_WS_TRANSPORT in globals(): force websocket relay
    - __BRYTHON__ in globals(): select the browser-compatible websocket layer
    - explicit parameter if provided
    - otherwise the default native socket path
    """
    if "FORCE_WS_TRANSPORT" in globals():
        return "WEB_SOCKET_RELAY"
    if "__BRYTHON__" in globals():
        return "WEB_COMPAT_WS"

    normalized = _normalize_code(param1)
    if not normalized or normalized == "AUTO":
        return "SOCKET"
    if normalized in {"SOCKET", "WS", "WEB_SOCKET_RELAY", "WEB_COMPAT_WS"}:
        return normalized
    return normalized


def build_netlayer_from_module(pymod):
    # Extract the functions
    f1 = getattr(pymod, 'get_server_flag')
    f2 = getattr(pymod, 'start_comms')
    f3 = getattr(pymod, 'send_to_server')
    f4 = getattr(pymod, 'broadcast_to_clients')
    f5 = getattr(pymod, 'register_mediator')
    f6 = getattr(pymod, 'shutdown_comms')
    dict_repr_netlayer = {
        'get_server_flag': f1,
        'start_comms': f2,
        'send_to_server': f3,
        'broadcast_to_clients': f4,
        'register_mediator': f5,
        'shutdown_comms': f6
    }
    return Objectifier(**dict_repr_netlayer)


def build_netlayer(param1="auto", param2="client"):
    """
    Helps retrieving functions from a particular netw_* module,
    based on the two given parameters.
    :param param1: info about the context/technology such as 'auto', 'socket', 'ws',
                   or a custom registered transport layer code
    :param param2: either 'client' or 'server', nothing else
    :return: a dictionary of functions
    """
    print('internal PYV init step:<build_netlayer Func>, params:', param1, param2)

    normalized_role = _normalize_code(param2)
    if normalized_role not in {"CLIENT", "SERVER"}:
        raise ValueError(f"param2 must be 'client' or 'server', got: {param2!r}")
    normalized_role = normalized_role.lower()

    transport_code = resolve_transport_code(param1)
    layer_spec = _TRANSPORT_LAYER_SPECS.get(transport_code)
    if layer_spec is None:
        raise ValueError(
            f"No transport layer definition module suitable for code: {transport_code!r}. "
            f"Known codes: {', '.join(sorted(_TRANSPORT_LAYER_SPECS))}"
        )

    module_name = layer_spec.get(normalized_role)
    if not module_name:
        raise ValueError(
            f"Transport layer code {transport_code!r} does not define a {normalized_role} backend"
        )

    resulting_netlayer = build_netlayer_from_module(
        importlib.import_module('.netw_strategies.'+module_name, package='pyved_engine.umediator')
    )
    return resulting_netlayer
