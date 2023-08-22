import random

from .TetColors import TetColors


MONOCHROM = TetColors.Pink


class TetPiece:
    # -- L-shaped pieces made of 3 blocks
    SM_L_SW = {
        "tiles": ((0, 0), (0, 1), (1, 1)),
        "x_adj": 1, "y_adj": 1,
        "color": MONOCHROM
    }
    SM_L_NW = {
        "tiles": ((0, 1), (0, 0), (1, 0)),
        "x_adj": 1, "y_adj": 1,
        "color": MONOCHROM
    }
    SM_L_NE = {
        "tiles": ((0, 0), (1, 0), (1, 1)),
        "x_adj": 1, "y_adj": 1,
        "color": MONOCHROM
    }
    SM_L_SE = {
        "tiles": ((1, 0), (1, 1), (0, 1)),
        "x_adj": 1, "y_adj": 1,
        "color": MONOCHROM
    }

    # -- L-shaped pieces made of 5 blocks
    L_SW = {
        "tiles": ((0, 0), (0, 1), (0, 2), (1, 2), (2, 2)),
        "x_adj": 2, "y_adj": 2,
        "color": MONOCHROM
    }
    L_NW = {
        "tiles": ((0, 2), (0, 1), (0, 0), (1, 0), (2, 0)),
        "x_adj": 2, "y_adj": 2,
        "color": MONOCHROM
    }
    L_NE = {
        "tiles": ((0, 0), (1, 0), (2, 0), (2, 1), (2, 2)),
        "x_adj": 2, "y_adj": 2,
        "color": MONOCHROM
    }
    L_SE = {
        "tiles": ((2, 0), (2, 1), (2, 2), (1, 2), (0, 2)),
        "x_adj": 2, "y_adj": 2,
        "color": MONOCHROM
    }

    # -- Bars of length 3, 4, 5
    BAR3_H = {
        "tiles": ((0, 0), (1, 0), (2, 0)),
        "x_adj": 2, "y_adj": 0,
        "color": MONOCHROM
    }
    BAR4_H = {
        "tiles": ((0, 0), (1, 0), (2, 0), (3, 0)),
        "x_adj": 3, "y_adj": 0,
        "color": MONOCHROM
    }
    BAR5_H = {
        "tiles": ((0, 0), (1, 0), (2, 0), (3, 0), (4, 0)),
        "x_adj": 4, "y_adj": 0,
        "color": MONOCHROM
    }

    BAR3_V = {
        "tiles": ((0, 0), (0, 1), (0, 2)),
        "x_adj": 0, "y_adj": 2,
        "color": MONOCHROM
    }
    BAR4_V = {
        "tiles": ((0, 0), (0, 1), (0, 2), (0, 3)),
        "x_adj": 0, "y_adj": 3,
        "color": MONOCHROM
    }
    BAR5_V = {
        "tiles": ((0, 0), (0, 1), (0, 2), (0, 3), (0, 4)),
        "x_adj": 0, "y_adj": 4,
        "color": MONOCHROM
    }

    # -- Squares of size 1, 2, 3
    SQUARE1 = {
        "tiles": ((0, 0),),
        "x_adj": 0, "y_adj": 0,
        "color": MONOCHROM
    }
    SQUARE2 = {
        "tiles": (
            (0, 0), (1, 0),
            (0, 1), (1, 1)
        ),
        "x_adj": 1, "y_adj": 1,
        "color": MONOCHROM
    }
    SQUARE3 = {
        "tiles": (
            (0, 0), (1, 0), (2, 0),
            (0, 1), (1, 1), (2, 1),
            (0, 2), (1, 2), (2, 2)
        ),
        "x_adj": 2, "y_adj": 2,
        "color": MONOCHROM
    }

    # R_SHAPE = {"tiles": ((0, 0), (1, 0), (0, 1), (0, 2)),
    #            "x_adj": 1,
    #            "y_adj": 2,
    #            "color": MONOCHROM}  # TetColor.ORANGE}
    #
    # T_SHAPE = {"tiles": ((0, 0), (1, 0), (1, 1), (2, 0)),
    #            "x_adj": 2,
    #            "y_adj": 1,
    #            "color": MONOCHROM}  # TetColor.MAGENTA}
    #
    # S_SHAPE = {"tiles": ((0, 0), (0, 1), (1, 1), (1, 2)),
    #            "x_adj": 1,
    #            "y_adj": 2,
    #            "color": MONOCHROM}  # TetColor.BLUE}

    # EX. TETRIS
    # Z_SHAPE = {"tiles": ((0, 0), (1, 0), (1, 1), (2, 1)),
    #            "x_adj": 2,
    #            "y_adj": 1,
    #            "color": MONOCHROM}

    # - new shapes, for the bloku doku
    # I_SHAPE_H = {
    #     "tiles": ((0, 0), (1, 0), (2, 0), (3, 0)),
    #     "x_adj": 3,
    #     "y_adj": 0,
    #     "color": MONOCHROM
    # }  # TetColor.RED}
    # I_SHAPE_V = {
    #     "tiles": ((0, 0), (0, 1), (0, 2), (0, 3)),
    #     "x_adj": 0,
    #     "y_adj": 3,
    #     "color": MONOCHROM
    # }

    @classmethod
    def gen_random(cls):
        omega = (  # 17 pieces
            cls.SM_L_SW,
            cls.SM_L_NW,
            cls.SM_L_NE,
            cls.SM_L_SE,

            cls.L_SW,
            cls.L_NW,
            cls.L_NE,
            cls.L_SE,

            cls.BAR3_H,
            cls.BAR4_H,
            cls.BAR5_H,
            cls.BAR3_V,
            cls.BAR4_V,
            cls.BAR5_V,

            cls.SQUARE1,
            cls.SQUARE2,
            cls.SQUARE3
        )
        sh = random.choice(omega)
        return cls(0, 0, sh, sh["color"])

    def __init__(self, x, y, shape, color, rot=0):
        self._coordi = x
        self._coordj = y
        self.shape = shape
        self._color = color
        self.rotation = rot

    @property
    def color(self):
        return self._color

    def get_area(self):
        return (1 + self.shape["x_adj"]) * (1 + self.shape["y_adj"])

    def move(self, x, y):
        self._coordi += x
        self._coordj += y

    # def get_gamecoords_infos(self):
    #     res = list()
    #     for t in self:
    #         res.append(t)  # [self._coordi, self._coordj
    #     return res

    def savecolor_in_grid(self, v):
        for x, y in self:
            v.render_tile(x, y, self.color)

    def __iter__(self):
        for x_offset, y_offset in self.shape["tiles"]:
            if self.rotation == 0:
                yield self._coordi + x_offset, self._coordj + y_offset
            elif self.rotation == 1:
                yield (self._coordi - y_offset + self.shape["y_adj"],
                       self._coordj + x_offset)
            elif self.rotation == 2:
                yield (self._coordi - x_offset + self.shape["x_adj"],
                       self._coordj - y_offset + self.shape["y_adj"])
            elif self.rotation == 3:
                yield (self._coordi + y_offset,
                       self._coordj - x_offset + self.shape["x_adj"])
