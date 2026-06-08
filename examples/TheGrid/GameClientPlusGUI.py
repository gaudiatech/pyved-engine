from . import glvars

# because we'll use the shared_code, we have to copy the ref from glvars to netcode.shared_code.glvars
from .netcode.shared_code import glvars as netcode_glvars
pyv = netcode_glvars.pyv = glvars.pyv

from .netcode.shared_code.NetwReadyModel import NetwReadyModel


E_COLOR = {'p1': 'blue', 'p2': 'red', 'ai': 'green'}


class GameClientPlusGUI:
    def __init__(self, player_sym):
        self.mediator = glvars.mediator
        self.mediator.register('x_notify_new_state', self.on_x_notify_new_state)
        self.mediator.register('paint', self.on_paint)

        self._model = NetwReadyModel(player_sym)
        self.ft = pyv.new_font_obj(None, 28)
        self.scorep1_label = None
        self.scorep1_label = None
        self._update_labels()

    @property
    def local_player(self) -> str:
        return self._model.localplayer

    @property
    def player_location(self) -> tuple:
        return self._model.positions[self.local_player]

    def _update_labels(self):
        self.scorep1_label = self.ft.render('p1:' + str(self._model.score['p1']), False, 'darkblue')
        self.scorep2_label = self.ft.render('p2:' + str(self._model.score['p2']), False, 'darkblue')

    def force_sync(self):
        self._model.force_sync()

    def request_move(self, wanted_cell):
        possib = self._model.get_possible_mvt(self.local_player)
        print(wanted_cell)
        if wanted_cell in possib:
            self._model.remote_move_pl(*wanted_cell)
        else:
            print('ignored mvt to blocked cell')

    # -------------------------
    # callbacks
    # -------------------------
    def on_x_notify_new_state(self, evcontent):
        print(f' client {self.mediator.ident} va charger un state!')
        self._model.load_state(evcontent)
        self._update_labels()

    def on_paint(self, evcontent):
        glvars.screen.fill('gray')
        cellsize = 64
        p1_pos = self._model.positions['p1']
        p2_pos = self._model.positions['p2']
        ai_pos = self._model.positions['ai']
        # draw squares + entities
        for lig in range(4):
            for c in range(6):
                a, b = c * 64, lig * 64
                pyv.draw_rect(
                    glvars.screen, glvars.CELL_COLOR,
                    (a, b, cellsize - 1, cellsize - 1),
                    0  # filled shape
                )
                if c == p1_pos[0] and lig == p1_pos[1]:
                    pyv.draw_rect(
                        glvars.screen, E_COLOR['p1'],
                        (a, b, 30, 30), 6  # line width 6
                    )
                elif c == p2_pos[0] and lig == p2_pos[1]:
                    pyv.draw_rect(
                        glvars.screen, E_COLOR['p2'],
                        (a, b, 30, 30), 6
                    )
                elif c == ai_pos[0] and lig == ai_pos[1]:
                    pyv.draw_circle(
                        glvars.screen, E_COLOR['ai'],
                        (a + 24, b + 24), 16, 0
                    )
        # add labels
        glvars.screen.blit(self.scorep1_label, (80, 270))
        glvars.screen.blit(self.scorep2_label, (290, 270))
