# import sys
# import traceback

# - avoid relative import for brython -
# from .... import engine as kataen
from .. import _hub as injec


def enum_builder_generic(to_upper, starting_index, *sequential, **named):
    domaine = range(starting_index, len(sequential) + starting_index)
    enums = dict(zip(sequential, domaine), **named)
    tmp_inv_map = {v: k for k, v in enums.items()}
    tmp_all_codes = domaine

    if to_upper:
        tmp = dict()
        for k, v in enums.items():
            if k == 'inv_map' or k == 'all_codes':
                continue
            tmp[k.upper()] = v
        enums = tmp

    enums['inv_map'] = tmp_inv_map
    enums['all_codes'] = tmp_all_codes
    enums['last_code'] = len(sequential) + starting_index - 1
    return type('Enum', (), enums)


def enum_builder_nplus(n, *sequential, **named):
    return enum_builder_generic(False, n, *sequential, **named)


def enum(*sequential, **named):
    """
    the most used enum builder
    """
    return enum_builder_nplus(0, *sequential, **named)


class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Also, the decorated class cannot be
    inherited from. Other than that, there are no restrictions that apply
    to the decorated class.

    To get the singleton instance, use the `instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    """

    def __init__(self, decorated):
        self._decorated = decorated

    def instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)


class Stack:
    def __init__(self, given_seq=None):
        if given_seq is None:
            self.fifo_list = []
        else:
            self.fifo_list = list(given_seq)

    def push(self, element):
        self.fifo_list.append(element)
        # - debug
        # print()
        # print('PUSH')
        # print('etat de pile {}'.format(self.fifo_list))

    def top_down_trav(self):
        return reversed(self.fifo_list)

    def bottom_up_trav(self):
        return self.fifo_list

    def pop(self):
        try:
            tmp = self.fifo_list.pop()
            res = tmp
        except IndexError:
            res = None  # the stack's already empty

        return res

    def peek(self):
        try:
            return self.fifo_list[-1]
        except IndexError:
            return None  # the stack's empty

    def count(self):
        return len(self.fifo_list)


class Tree:
    def __init__(self, root_content):
        self.root = TreeNode(root_content, None)
        self.__allnodes = set()
        self.__allnodes.add(self.root)

    def add_content(self, content, parent_node):
        if parent_node not in self.__allnodes:
            raise ValueError('cannot find specified parent_node')

        n = TreeNode(content, parent_node)
        parent_node.childs.append(n)
        self.add_node(n)

    def add_node(self, n_val):
        raise NotImplementedError  # TODO complete this implem.

    def count(self):
        return len(self.__allnodes)

    def get_node_by_content(self, searched_content):
        queue = [self.root]
        while len(queue) > 0:
            exn = queue.pop()
            if searched_content == exn.content:
                return exn
            if not exn.is_leaf():
                queue.extend(exn.childs)
        return None

    def cut_from_node(self, ref_node):
        if ref_node == self.root:
            raise ValueError('empty tree not allowed')

        if not ref_node.is_leaf():
            # if node has childs, we shall cut the whole branch
            for c in ref_node.childs:
                self.cut_from_node(c)

        ref_node.parent.childs.remove(ref_node)
        self.__allnodes.remove(ref_node)


class TreeNode:
    def __init__(self, content, parent):
        self.childs = list()
        self.content = content
        self.parent = parent

    def is_leaf(self):
        return len(self.childs) == 0


@Singleton
class StContainer:
    """
    contient toutes les instances de classes qui dérivent de BaseGameState
    """

    def __init__(self):
        self.__setup_done = False
        self.assoc_id_state_obj = dict()

    def hack_bios_state(self, gs_obj):
        self.assoc_id_state_obj[-1] = gs_obj

    def setup(self, enum_game_states, stmapping, pymodule=None):
        self.__setup_done = True

        """
        - deprecated & disabled: auto-load kata service state
        if -1 in stmapping.keys():
            gs_obj = stmapping[-1]  # constructor KataFrameState -> __init__(-1, 'KataFrame')
            gs_obj.glvars_module = pymodule
            self.hack_bios_state(gs_obj)
        """
        # - debug
        print('* * * in setup  ')
        print('enum_game_states= ' + str(enum_game_states))
        print('stmapping= ' + str(stmapping))

        # - initialisation d'après paramètre type: core.enum
        if stmapping:  # but = charger la classe deja identifiee en memoire
            for state_ident, adhoc_cls in stmapping.items():
                obj = adhoc_cls(state_ident, adhoc_cls.__name__)
                self.assoc_id_state_obj[state_ident] = obj
        else:

            # old code
            for id_choisi, nom_etat in enum_game_states.inv_map.items():
                class_name = nom_etat + 'State'
                self._auto_find_statecls(id_choisi, nom_etat, class_name)

    def _auto_find_statecls(self, id_choisi, nom_etat, nom_cls):
        pymodule_name = injec.underscore_format(nom_etat)
        pythonpath = 'app.{}.state'.format(pymodule_name)
        print('StContainer is loading a new game state...')
        try:
            pymodule = __import__(pythonpath, fromlist=[nom_cls])
            adhoc_cls = getattr(pymodule, nom_cls)  # class has been retrieved -> ok

            obj = adhoc_cls(id_choisi, nom_etat)
            self.assoc_id_state_obj[id_choisi] = obj

        except ImportError as exc:
            print('adhoc module name(conv. to underscore format)={}'.format(pymodule_name))
            print('full path for finding class={}'.format(pythonpath))
            print('target class={}'.format(nom_cls))

            print('WEB CONTEXT WARNING: make sure you dont have a file named app.py in your project!')
            # avoid trouble with Brython...
            # sys.stderr.write("Error: failed to import class {} (info= {})\n".format(nom_cl, exc))
            # traceback.print_last()

    def retrieve(self, identifiant):
        """
        :param identifiant: peut-être aussi bien le code (int) que le nom de classe dédiée (e.g. PlayState)
        :return: instance de BaseGameState
        """

        # construction par nom ou identifiant entier
        # TODO rétablir recherche par nom et non par code...

        # if isinstance(identifiant, str):
        #     gamestate_id = None
        #     for num_id, nom in state_listing.items():
        #         if nom == identifiant:
        #             gamestate_id = num_id
        #             break
        #     if gamestate_id is None:
        #         assert 0, "state name not found: " + identifiant
        # else:
        #     gamestate_id = identifiant
        gamestate_id = identifiant
        return self.assoc_id_state_obj[gamestate_id]
