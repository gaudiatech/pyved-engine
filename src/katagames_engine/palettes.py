class _Pal:
    def __init__(self, pal_tuple):
        self.dict = dict()
        self.listing = list()
        for elt in pal_tuple:
            t3 = (elt[1], elt[2], elt[3])
            self.dict[elt[0]] = t3
            self.listing.append(t3)

    def __getitem__(self, item):
        if isinstance(item, str):
            return self.dict[item]
        else:
            return self.listing[item]


# -------------------
#  toutes les definitions
# -------------------
_c64pdef = (  # Commodore 64
    ('black', 0, 0, 0),
    ('white', 255, 255, 255),
    ('red', 138, 20, 22),
    ('cyan', 120, 170, 207),

    ('violet', 204, 68, 204),
    ('green', 100, 184, 70),
    ('blue', 69, 32, 195),
    ('yellow', 207, 207, 101),

    ('orange', 154, 101, 32),
    ('brown', 101, 69, 0),
    ('lightred', 207, 138, 101),
    ('darkgrey', 69, 69, 69),

    ('grey', 138, 138, 138),
    ('lightgreen', 170, 239, 138),
    ('lightblue', 160, 162, 255),
    ('lightgrey', 170, 170, 170),

    # {101,170,207}
    # {138,69,170}
    # {101,170,69}
    # {69,32,170}	{}	{138,101,32}	{}	{}{}	{}	{138,101,223}
)

c64 = _Pal(_c64pdef)
