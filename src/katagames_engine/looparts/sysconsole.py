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
        # better not use wrapper cause its lagging in web ctx!

        #self.wrapper_obj = textwrap.TextWrapper(break_long_words=True)
        bounds = _hub.ascii.get_bounds()
        #self.wrapper_obj.width = bounds[0] - 2  # minus 2 because we have a 1-cell border left&right
        #
        self.txtcolor = txtcolor

        # model per se
        self.logical_cursor_pos = [0, 0]
        self.maxlines = bounds[1] - 3  # see above, almost same remark
        self.alltext = ''
        self.lines = list()
        self._nblines = 0

    def output(self, word_or_letter):
        """
        for better results, use full lines!
        :param word_or_letter:
        :return:
        """

        # # TODO need to split lines
        # curr_card_lines = len(self.lines)
        # self.alltext += word_or_letter
        # tmp = self.wrapper_obj.wrap(self.alltext)
        # if len(tmp) > curr_card_lines:
        #     self.lines = tmp
        # else:
        #     self.lines[-1] += word_or_letter
        self.lines.append(word_or_letter)
        self._nblines += 1

    @property
    def nblines(self):
        return self._nblines

    def updategfx(self):
        # only take a chunk, => achieve scrolling
        partial_lines = self.lines[-self.maxlines:]

        for line_rank, line_content in enumerate(partial_lines):
            put_line(  # if we dont use bgcolor => pass None
                line_content, (self.CONS_DISP_OFFSET[0], self.CONS_DISP_OFFSET[1]+line_rank), self.txtcolor, None
            )
        _hub.ascii.flush()
