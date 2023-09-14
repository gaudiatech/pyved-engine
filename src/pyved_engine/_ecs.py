"""
ECS (Entity-Component-System) is an architectural pattern commonly used in game development
to structure the organization and behavior of entities within a game. It provides a flexible
and scalable approach to handle complex game systems and interactions.
"""


# 15 functions/procudures here


_components = {}
_archetypes = {}
# TODO structure scene by scene
_entities = []
_systems = []


# Entity functions -----
def new_entity():
    entity = {}
    _entities.append(entity)
    return entity


def delete_entity(entity):
    _entities.remove(entity)


def wipe_entities():
    del _entities[:]


def init_entity(entity, values):
    entity.update(values)


def dissect_entity(given_ent, keys_li):
    return [given_ent[k] for k in keys_li]


# Component functions -----
def add_component(entity, component_name, data, bypass=False):
    if not bypass and component_name == 'Archetype':
        raise ValueError('ERR: Cannot declare a component named "Archetype"!')

    component = {component_name: data}
    entity.update(component)
    if component_name not in _components:
        _components[component_name] = []
    _components[component_name].append(entity)


def remove_component(entity, component_name):
    if component_name in entity:
        entity.pop(component_name)
        if component_name in _components:
            _components[component_name].remove(entity)


# System functions -----
def add_system(system_func):
    # print('  added system:', system_func)
    _systems.append(system_func)


def bulk_add_systems(module):
    """
    a procedure (hacky but very convenient) to add all systems directly from a module
    :param module: Python module that contains all of your game-specific 'system_func' items
    """
    names = module.__all__ if hasattr(module, '__all__') else dir(module)
    bulk = [name for name in names if not name.startswith('_')]
    for syst_name in bulk:
        add_system(getattr(module, syst_name))


def remove_system(system_func):
    _systems.remove(system_func)


def systems_proc():
    if len(_systems):
        for system_func in _systems:
            system_func(_entities, _components)
    else:
        raise ValueError('[PYV/ecs] systems_proc func called, but no systems has been added')


# Archetype functions -----
def new_from_archetype(archetype_name):
    if archetype_name not in _archetypes:
        raise KeyError(f"ERR: Archetype {archetype_name} is not valid!")

    entity = new_entity()
    for component_name in _archetypes[archetype_name]:
        add_component(entity, component_name, None)
    add_component(entity, 'Archetype', archetype_name, bypass=True)

    return entity


def define_archetype(archetype_name, component_names):
    _archetypes[archetype_name] = component_names


def find_by_components(*compokeys):
    """
    this func will return all entities that satisfy each on of compokeys (=has that list of components in it)
    :param compokeys:
    :return: a list
    """
    res = list()

    for entity in _entities:
        compat = True
        for c in compokeys:
            if c not in entity:
                compat = False
                break
        if compat:
            res.append(entity)
    return res


def all_entities(scene=None):
    # TODO fetch from a given scene ...
    return iter(_entities)


def has_archetype(entity, archetype_name):
    if 'Archetype' not in entity:
        return False
    return entity['Archetype'] == archetype_name


def find_by_archetype(archetype_name):
    return list(filter(lambda e: has_archetype(e, archetype_name), _entities))

    # res = list()
    # for entity in _entities:
    #     if 'Archetype' in entity:
    #         if entity['Archetype'] == archetype_name:
    #             res.append(entity)
    # if not len(res):
    #     raise KeyError(f'ERR: Cannot find archetype {archetype_name}!')
    # return res


def list_all_archetypes():
    return tuple(_archetypes.keys())


def archetype_of(entity_ref):  # we simply extract the archetype
    if 'Archetype' not in entity_ref:
        return None
    return entity_ref['Archetype']
