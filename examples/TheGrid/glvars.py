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
CELL_COLOR = 33, 33, 50
game_paused = False

mediator = None

scr_size = (192*2, 256+50)  # because cells are 64x64 pixels and matrx is 6 columns x 4 lines, +50 for the text

screen = None  # to be init by pygame
game_over = False
