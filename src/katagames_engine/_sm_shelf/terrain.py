import abc


# --- trick from stackoverflow...
class abstractclassmethod(classmethod):
    __isabstractmethod__ = True

    def __init__(self, callable):
        callable.__isabstractmethod__ = True
        super(abstractclassmethod, self).__init__(callable)


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
                if not self.__class__.isValidValue(elt):
                    raise ValueError('val type doesnt match matrix type, elt={}'.format(elt))
            self.repr_1d = li1d_val_init
        else:
            self.repr_1d = [self.__class__.defaultValue()] * nb_elem

    @abstractclassmethod
    def defaultValue(cls):
        pass

    @abstractclassmethod
    def isValidValue(cls, val):
        pass

    def get_val(self, i, j):
        if self.is_out(i, j):
            raise ValueError('coords {} {} out of bounds for the current matrix'.format(i, j))
        adhoc_ind = j * self.width + i
        return self.repr_1d[adhoc_ind]

    def set_val(self, i, j, val):
        if not self.__class__.isValidValue(val):
            raise ValueError(
                'val {} incompatible avec le type de matrice utilisé ({})'.format(val, self.__class__.__name__)
            )
        ind = j * self.width + i
        self.repr_1d[ind] = val

    def set_all(self, val):
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


class BoolMatrix(BaseMatrix):
    # --- redefinition de 2 methodes venant den haut
    @classmethod
    def defaultValue(cls):
        return True

    @classmethod
    def isValidValue(cls, val):
        return isinstance(val, bool)


class IntegerMatrix(BaseMatrix):
    """
    modélise une matrice d'entiers. Par défaut, toutes les cellules sont à 0
    """

    # --- redefinition de 2 methodes venant den haut
    @classmethod
    def defaultValue(cls):
        return 0

    @classmethod
    def isValidValue(cls, val):
        return (val is None) or isinstance(val, int)


class DijkstraPathfinder:
    @staticmethod
    def find_path(espace_matr, source_pos, dest_pos, limitations_wh=None):
        """
        :param espace_matr:
        :param source_pos:
        :param dest_pos:
        :param limitations_wh:
        :return: soit None, soit une liste de coords
        """
        chemin_inv = dict()  # on anticipe le backtrace code, en vue de retourner le plus court chemin
        candidats = set()
        src = tuple(source_pos)
        dest = tuple(dest_pos)

        # --- initialisation distance à tous les pts
        dist = dict()
        if limitations_wh:
            limit_x, limit_y = limitations_wh
        else:
            limit_x, limit_y = espace_matr.get_size()

        binf_x, bsup_x = src[0] - limit_x, src[0] + limit_x
        binf_y, bsup_y = src[1] - limit_y, src[1] + limit_y
        for x in range(binf_x, bsup_x + 1):
            for y in range(binf_y, bsup_y + 1):
                k = (x, y)
                if espace_matr.is_out(*k):
                    continue
                dist[k] = 99999
                candidats.add(k)
        dist[src] = 0

        visited = set()  # représente l'ensemble des sommets déjà visités

        while len(candidats) > 0:
            # select the element of Q with the min. distance
            # cest à dire on va explorer le sommet listé dans Q, de distance minimale
            dist_minimale = 999999
            u = None
            for sommet_a_explorer in candidats:
                if dist[sommet_a_explorer] < dist_minimale:
                    dist_minimale = dist[sommet_a_explorer]
                    u = sommet_a_explorer

            # on indique que u est exploré
            candidats.remove(u)
            visited.add(u)

            # exploration : calcul des voisins de u
            voisins = list()
            les_possib = [
                (u[0] - 1, u[1]),
                (u[0] + 1, u[1]),
                (u[0], u[1] + 1),
                (u[0], u[1] - 1),
            ]
            for k in les_possib:
                if espace_matr.is_out(*k):
                    continue
                if not (binf_x <= k[0] <= bsup_x):
                    continue
                if not (binf_y <= k[1] <= bsup_y):
                    continue
                if espace_matr.get_val(*k):
                    continue  # blocage
                voisins.append(k)

            for v in voisins:  # m-à-j plus courtes distances pr arriver à v
                w = 1
                if dist[v] > dist[u] + w:
                    dist[v] = dist[u] + w
                    chemin_inv[v] = u

        # tous les candidats ont été testés => backtrace code c-à-d reconstruction chemin le + court
        chemin = [dest]
        x = dest
        no_way = False
        while x != src:
            if x not in chemin_inv:
                no_way = True
                break
            x = chemin_inv[x]
            chemin.insert(0, x)  # insertion en 1ère position

        if no_way:
            return None
        return chemin
