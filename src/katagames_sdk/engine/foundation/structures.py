

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


def enum_builder(*sequential, **named):
    """
    the most used enum builder
    """
    return enum_builder_nplus(0, *sequential, **named)


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
