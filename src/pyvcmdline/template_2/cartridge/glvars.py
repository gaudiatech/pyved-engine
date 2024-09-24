# ------
# engine-related code, do not modify!
# --------


registry = set()
libname_to_alias_mapping = dict()


def get_alias(origin_lib_name):
    return libname_to_alias_mapping[origin_lib_name]


def has_registered(origin_lib_name):
    return origin_lib_name in libname_to_alias_mapping


def register_lib(alias, libname, value):  # handy for dependency injection
    global registry, libname_to_alias_mapping
    libname_to_alias_mapping[libname] = alias
    if alias in registry:
        raise KeyError(f'Cannot register lib "{alias}" more than once!')
    globals()[alias] = value
    registry.add(alias)


# ------
# custom code the gamedev added
# --------

screen = None
t_now = None
t_last_update = None
world = None
terrain = None

WIDTH = 960
HEIGHT = 720
SCR_SIZE = (WIDTH, HEIGHT)

BLOCKSIZE = 40
BLOCK_SPEED = 100.0
AVATAR_SIZE = 38
AV_SPEED = 330.0
JUMP_POWER = 582.0
SPEED_CAP = 700.0
SPAWN = -1080, 400
