from . import pimodules
pyv = pimodules.pyved_engine


# alias
GuiButton = pyv.gui.Button
# constructor, FYI= def __init__(self, pos=None, size=None, label='bt_label')


class PopupPromotion(pyv.EvListener):
    """
    listens for a single event, when it happens this view cls will draw a Popup from which the player can choose
    the piece he/she wants.
    Careful: should be used only for a human player!
    """
    POPUP_SCR_COORDS = (505, 180)
    POPUP_DIM = (360, 200)
    BG_COLOR = 'antiquewhite4'

    def __init__(self, refmod):
        super().__init__()
        self._mod = refmod
        self._target_square_promo = [6, 1]  # tmp: for debug, we have set A2 ... # should be None

        self._popup_on = False
        self._ft_big = pyv.pygame.font.Font(None, 28)
        self._ft = pyv.pygame.font.Font(None, 24)
        bx, by = self.POPUP_SCR_COORDS
        self.padding_vals = (10, 10)  # padding for the whole popup content
        px, py = self. padding_vals
        self.ico_order = ('queen', 'rook', 'bishop', 'knight')  # chosen standard

        # Idea: I'm using a 3-line LAYOUT for Gui elements
        # line0: will paste the what to do label...
        self.what_to_do_lbl = self._ft_big.render('Select a piece to promote your pawn', True, 'darkred')

        # line1: will paste clickable icons
        xspacing = 105
        self.yoffset_line1 = dc1 = 45
        self.buttons = {
            'queen': GuiButton(pos=(bx + px + self.ico_order.index('queen')*xspacing, by + py + dc1) ),
            'rook': GuiButton(pos=(bx + px + self.ico_order.index('rook')*xspacing, by + py + dc1) ),
            'bishop': GuiButton(pos=(bx + px + self.ico_order.index('bishop')*xspacing, by + py + dc1) ),
            'knight': GuiButton(pos=(bx + px + self.ico_order.index('knight')*xspacing, by + py + dc1) ),
        }
        # update the img, to have nice icons...
        curr_color = self._mod.get_curr_player()
        for ke, button_obj in self.buttons.items():
            ref_img = pyv.vars.images[curr_color+'_'+ke]
            cloned_img = ref_img.copy()  # create copy so if img is modified -> np
            button_obj.set_image(cloned_img)

        # line2 : will paste labels/the legend, piece by piece
        self.yoffset_line2 = 155
        self.label = {
            'queen': self._ft.render('Queen', True, 'black'),
            'rook': self._ft.render('Rook', True, 'black'),
            'bishop': self._ft.render('Bishop', True, 'black'),
            'knight': self._ft.render('Knight', True, 'black'),
        }
        self.label_xoffset = {
            'queen': 0,
            'rook': 1*xspacing,
            'bishop': 2*xspacing,
            'knight': 3*xspacing
        }

    def on_promotion_popup(self, ev):
        if self._mod.fetch_player_type(ev.plcolor) == 'AI':
            # the AI will always promote to queen
            self._mod.get_board().promote(ev.target_square, 'queen')
        else:
            # the human can choose!
            self._popup_on = True
            self._target_square_promo = ev.target_square

    def _is_piece_selected(self, mpos):
        for ke, button_obj in self.buttons.items():
            if button_obj.rect.collidepoint(mpos):
                return ke

    def on_mousedown(self, ev):
        # once clicked, if popup was open we check if smth (one chess piece) was indeed selected
        if self._popup_on:
            y = self._is_piece_selected(ev.pos)
            if y:
                print('clicked:', y)
                self._mod.get_board().promote(self._target_square_promo, y)
                self._popup_on = False
            else:
                print('please click smth')

    def on_paint(self, ev):
        if not self._popup_on:
            return
        # border & bg
        x, y = self.POPUP_SCR_COORDS
        dim0, dim1 = self.POPUP_DIM
        pyv.pygame.draw.rect(ev.screen, self.BG_COLOR, (x, y, dim0, dim1), 0)
        pyv.pygame.draw.rect(ev.screen, 'darkgray', (x, y, dim0, dim1), 2)
        padx, pady = self.padding_vals

        # line0
        ev.screen.blit(self.what_to_do_lbl, (x+padx, y+pady))

        # line1
        for e in self.ico_order:
            widget = self.buttons[e]
            ev.screen.blit(widget.image, widget.rect.topleft)

        # line2:
        # (label for each piece)
        k = self.yoffset_line2
        for e in self.ico_order:
            ev.screen.blit(
                self.label[e],
                (x + self.label_xoffset[e] + padx, k + y + pady)
            )
