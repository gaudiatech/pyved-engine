import abc


# --- trick from stackoverflow...
class abstractclassmethod(classmethod):
    __isabstractmethod__ = True

    def __init__(self, fcallable):
        callable.__isabstractmethod__ = True
        super(abstractclassmethod, self).__init__(fcallable)


class BaseMatrix(object):
    """
    classe ABSTRAITE
    représentation 1d dune matrice bidimensionnelle de taille connue
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, matr_size, li1d_val_init=None):
        self.width, self.height = matr_size
        nb_elem = self.width * self.height
        if li1d_val_init is not None:
            if len(li1d_val_init) != nb_elem:
                raise ValueError('val pour init matrice incoherentes')
            for elt in li1d_val_init:
                if not self.__class__.is_valid_val(elt):
                    raise ValueError('val type doesnt match matrix type, elt={}'.format(elt))
            self.repr_1d = li1d_val_init
        else:
            self.repr_1d = [self.__class__.default_val()] * nb_elem

    @abstractclassmethod
    def default_val(cls):
        pass

    @abstractclassmethod
    def is_valid_val(cls, val):
        pass

    def get_val(self, i, j):
        if self.is_out(i, j):
            raise ValueError('coords {} {} out of bounds for the current matrix'.format(i, j))
        adhoc_ind = j * self.width + i
        return self.repr_1d[adhoc_ind]

    def set_val(self, i, j, val):
        if not self.__class__.is_valid_val(val):
            raise ValueError(
                'val {} incompatible avec le type de matrice utilisé ({})'.format(val, self.__class__.__name__)
            )
        ind = j * self.width + i
        self.repr_1d[ind] = val

    def set_all_values(self, val):
        for i in range(self.width):
            for j in range(self.height):
                self.set_val(i, j, val)

    def is_out(self, i, j):
        return not (0 <= i < self.width and 0 <= j < self.height)

    def get_size(self):
        return self.width, self.height

    def __str__(self):
        res = '{} x {} matrix'.format(self.width, self.height)
        res += "\n"
        for j in range(self.height):
            for i in range(self.width):
                ind = j * self.width + i
                res += '  {}'.format(self.repr_1d[ind])
            res += "\n"
        return res


class IntegerMatrix(BaseMatrix):
    """
    modélise une matrice d'entiers. Par défaut, toutes les cellules sont à 0
    """

    # --- redefinition de 2 methodes venant den haut
    @classmethod
    def default_val(cls):
        return None  # TODO faire en sorte que ce soit 0 mais faudra modifer RandomMaze avant cela

    @classmethod
    def is_valid_value(cls, val):
        return (val is None) or isinstance(val, int)
