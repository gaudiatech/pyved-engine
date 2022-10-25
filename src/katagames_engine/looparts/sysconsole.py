from .. import _hub
from ..compo import vscreen
import textwrap


pygame = _hub.pygame
_cached_scrref = None


def put_line(w, base_ij_pos, fgcolor, bgcolor):
    global _cached_scrref
    i, j = base_ij_pos
    chsize = _hub.ascii.get_charsize()
    if _cached_scrref is None:
        _cached_scrref = vscreen.screen

    # ----------
    #  ALGO 1: this would work well, but due to how ascii_web is created, we have to put char 1 by 1 directly to screen
    # ---------
    # sumsurf = pygame.Surface((len(w) * chsize, chsize))
    # tmpc = pygame.Color(fgcolor)
    # ck = pygame.Color((tmpc.r + 1) % 255, (tmpc.g + 1) % 255, (tmpc.b + 1) % 255)
    # sumsurf.fill(ck)
    # sumsurf.set_colorkey(ck)
    # for rank, char in enumerate(w):
    #     _hub.ascii.put_char(char, (rank, 0), fgcolor, bgcolor, dest_surf=sumsurf)

    # _cached_scrref.blit(sumsurf, (chsize * i, chsize * j))

    # ---------
    # ALGO 2
    # ---------
    starti, startj = base_ij_pos
    for rank, char in enumerate(w):
        _hub.ascii.put_char(char, (starti+rank, startj), fgcolor, bgcolor)
    _hub.ascii.flush()


class MiniConsComponent:
    """
    contains:
    - minimalistic model to handle the cursor pos
       + {backspace key; delete key; carret return}
    - a flush method that takes care of everything
       (useful to call everything that's internal to kengi.ascii)
    """
    CONS_DISP_OFFSET = (1, 1)  # cannot use 0 bc its a border!

    def __init__(self, txtcolor):
        self.txtcolor = txtcolor
        # the model per se
        self.changed = False
        self.logical_cursor_pos = [0, 0]
        bounds = _hub.ascii.get_bounds()
        self.maxlines = bounds[1] - 2  # see above, almost same remark
        self.alltext = ''
        self.lines = list()
        self._nblines = 0

    def output(self, line_of_txt):
        """
        for better results, use full lines!
        :param line_of_txt: type str, not longer than a line
        :return:
        """
        self.changed = True
        self.lines.append(line_of_txt)
        self._nblines += 1

    @property
    def nblines(self):
        return self._nblines

    def updategfx(self):
        # only take a chunk => achieve scrolling
        partial_lines = self.lines[-self.maxlines:]
        for line_rank, line_content in enumerate(partial_lines):
            put_line(  # since we dont use bgcolor => pass None
                line_content, (self.CONS_DISP_OFFSET[0], self.CONS_DISP_OFFSET[1]+line_rank), self.txtcolor, None
            )
        _hub.ascii.flush()
        self.changed = False
