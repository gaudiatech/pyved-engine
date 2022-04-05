import sys
sys.path.append("..\\..\\")
import katagames_engine as kengi
from events import MyEvTypes
import random


OMEGA_CODES = list(range(6))
C_EVIL, C_EMERALD, C_FIRESTONE, C_HEART, C_RUBY, C_STAR = OMEGA_CODES


class Grid(kengi.event.CogObj):
    WIDTH = 10
    HEIGHT = 7

    def __init__(self):
        self._content = [  # matrix-like
            [None for _ in range(self.WIDTH)] for _ in range(self.HEIGHT)
        ]
        self._randomize()

    def swap(self, c0, c1):
        print('swapping {} avec {}'.format(c0, c1))
        i0, j0 = c0
        i1, j1 = c1
        tmp = self._content[j0][i0]
        self._content[j0][i0] = self._content[j1][i1]
        self._content[j1][i1] = tmp
        self.test_explosion()

    def _tmp_func(self, cpos, lim, b, x=None, y=None):
        print(f'call tmp_func with cpos={cpos}, lim={lim}, b={b}')
        # returns info about explosion if it occurs
        if cpos+1 >= lim:
            return None
        cpos += 1
        if x is None and y is None:
            raise ValueError
        
        if y is not None:
            b.append(self._content[y][cpos])
        if x is not None:
            b.append(self._content[cpos][x])
        if len(b)<3:
            return self._tmp_func(cpos, lim, b, x, y)
        
        symc = b[0]
        efound = True
        for elt in b:
            if elt != symc:
                efound = False
                break
        if efound:
            return b
        else:
            del b[0]
            return self._tmp_func(cpos, lim, b, x, y)
    
    def test_explosion(self):
        print(' test explo')
        offset_a = [1, 0]
        offset_b = [0, 1]
        bsup_a, bsup_b = self.WIDTH, self.HEIGHT
        c_pos = [0, 0]
        buffer = list()
        e_horz = self._tmp_func(c_pos[0], bsup_a, buffer, y=0)
        if e_horz:
            return e_horz
        return False
    
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
        print('destroy:', li_pos)
        for elt in li_pos:
            self._content[elt[1]][elt[0]] = None

    def _randomize(self):
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


t = Grid()
print(t)
