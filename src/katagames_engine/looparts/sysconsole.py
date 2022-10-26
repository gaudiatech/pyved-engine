from .. import _hub

pygame = _hub.pygame


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
        self.fgcolor = txtcolor
        self.bgcolor = None  # for text !

        # the model per se
        self.needs_paint_op = False
        self.logical_cursor_pos = [0, 0]
        bounds = _hub.ascii.get_bounds()
        self.maxlines = bounds[1] - 2  # see above, almost same remark
        self.alltext = ''
        self.lines = list()
        self._nblines = 0
        self._buffer = list()
        self._prev_t = None

    def draw_console_line(self, myword, base_ij_pos):
        for rank, mchar in enumerate(myword):
            _hub.ascii.put_char(mchar, (base_ij_pos[0] + rank, base_ij_pos[1]), self.fgcolor, self.bgcolor)

    def lineappend(self, line_of_text):
        """
        for better results, use full lines! Its buffered bc we wanna
        add it line per line and display before adding the nxt one
        """
        self._buffer.append(line_of_text)

    def has_bufferempty(self):
        return len(self._buffer) == 0

    def update(self, infot):
        if len(self._buffer):
            self._prev_t = infot
            self.lines.append(self._buffer.pop(0))
            self.needs_paint_op = True

    def draw(self):
        # push the whole set of chars to screen & refresh display
        _hub.ascii.reset()
        if len(self.lines) > self.maxlines:
            k = self.maxlines
            plines = self.lines[-k:]  # last k lines
        else:
            plines = self.lines
        for j, line_content in enumerate(plines):
            self.draw_console_line(  # since we dont use bgcolor => pass None
                line_content, (self.CONS_DISP_OFFSET[0], self.CONS_DISP_OFFSET[1] + j)
            )
        _hub.ascii.flush()
        self.needs_paint_op = False
