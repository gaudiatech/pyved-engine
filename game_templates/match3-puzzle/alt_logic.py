import sys
sys.path.append("..\\..\\")
import katagames_engine as kengi
from alt_events import MyEvTypes
import random


OMEGA_CODES = list(range(6))
C_EVIL, C_EMERALD, C_FIRESTONE, C_HEART, C_RUBY, C_STAR = OMEGA_CODES


class Score(kengi.event.CogObj):
    def __init__(self):
        super().__init__()
        self.val = 0

    def record(self, comboinfo):
        self.val += 100 * len(comboinfo)
        self.pev(MyEvTypes.ScoreUpdate, value=self.val)

    def reset(self):
        self.val = 0
        self.pev(MyEvTypes.ScoreUpdate, value=0)


class Grid(kengi.event.CogObj):
    WIDTH = 10
    HEIGHT = 7

    def __init__(self):
        self._content = [  # matrix-like
            [None for _ in range(self.WIDTH)] for _ in range(self.HEIGHT)
        ]
        self.randomize()

    def swap(self, c0, c1):
        print('swapping {} avec {}'.format(c0, c1))
        i0, j0 = c0
        i1, j1 = c1
        tmp = self._content[j0][i0]
        self._content[j0][i0] = self._content[j1][i1]
        self._content[j1][i1] = tmp

    @staticmethod
    def _can_score(b):
        # returns list if 3+ combo exists, None otherwise 
        symc = b[0][1]
        efound = True
        cpt = -1
        total = len(b)
        for elt in b:
            if elt[1] == symc:
                cpt += 1
        if cpt >= 3:
            return list(b)

    @staticmethod
    def _all_alike(b):
        sym = b[0][1]
        for elt in b:
            if elt[1] != sym:
                return False
        return True

    def _greedexplo(self, cpos, lim, b, x, y):
        if x is None:
            cpos[0] += 1
            if cpos[0] >= lim:
                return b

        if y is None:
            cpos[1] += 1
            if cpos[1] >= lim:
                return b

        if self._content[cpos[1]][cpos[0]] == b[0][1]:
            b.append(
                (tuple(cpos), self._content[cpos[1]][cpos[0]])
            )
            return self._greedexplo(cpos, lim, b, x, y)
        return b
    
    def _findexplo(self, cpos, lim, b, x=None, y=None):
        """
        Returns info about explosion if it's found
        """
        if (x is None) and (y is None):
            raise ValueError('need to set either x or y')
        
        b.append((
            tuple(cpos),
            self._content[cpos[1]][cpos[0]]
        ))
        
        if len(b) >= 3:
            if b[0][1] is not None and self._all_alike(b):
                ret = self._greedexplo(cpos, lim, b, x, y)
                print(ret)
                return ret
            del b[0]

        if x is None:
            cpos[0] += 1
            if cpos[0] >= lim:
                return None

        if y is None:
            cpos[1] += 1
            if cpos[1] >= lim:
                return None
        
        return self._findexplo(cpos, lim, b, x, y)
    
    def test_explosion(self):
        """
        returns either None or a list of pos
        """
        buffer = list()

        for gy in range(self.HEIGHT):
            c_pos = [0, gy]
            e_horz = self._findexplo(c_pos, self.WIDTH, buffer, y=gy)
            if e_horz:
                return e_horz
            buffer.clear()

        for gx in range(self.WIDTH):
            c_pos = [gx, 0]
            e_vert = self._findexplo(c_pos, self.HEIGHT, buffer, x=gx)
            if e_vert:
                return e_vert
            buffer.clear()
    
    def can_swap(self, a, b):
        if a[0] != b[0] or a[1] != b[1]:
            if abs(a[0]-b[0])+abs(a[1]-b[1]) == 1:
                if self._content[a[1]][a[0]] != self._content[b[1]][b[0]]:
                    return True
        return False

    def destroy(self, li_pos):
        """
        given a list of (i,j) pos that need to be destroyed, destroy it and use gravity
        +gen new blocks
        """
        self.pev(MyEvTypes.Explosion, einfos=li_pos)

        print('destroying...')
        
        for elt in li_pos:
            self._content[elt[1]][elt[0]] = None

    def randomize(self):
        for j in range(self.HEIGHT):
            for i in range(self.WIDTH):
                self._content[j][i] = random.choice(OMEGA_CODES)

    def __iter__(self):
        """
        so we can loop over all symbols, without the need to handle i,j indices
        """
        tmp = list()
        for j in range(self.HEIGHT):
            for i in range(self.WIDTH):
                tmp.append(((i, j), self._content[j][i]))
        return tmp.__iter__()

    def __str__(self):
        res = ''
        for j in range(self.HEIGHT):
            for i in range(self.WIDTH):
                res += f' {self._content[j][i]} '
            res += '\n'
        return res


# - test
# t = Grid()
# print(t)
