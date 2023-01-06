import katagames_engine as kengi
from myrpg_defs import GameStates, MyEvTypes


BaseGameState = kengi.BaseGameState
EngineEvTypes = kengi.EngineEvTypes
pygame = kengi.pygame


class MenuScreenView(kengi.EvListener):

    def __init__(self, selected_option):
        super().__init__()
        self._bg_color = 'antiquewhite3'

        self.optioncode_to_pos = {
            0: (33, 100),
            1: (33, 180),
            2: (33, 260)
        }
        self.pos_cursor = self.optioncode_to_pos[selected_option]

        ft = pygame.font.Font(None, 19)
        txt_labels = {
            0: 'Travel the world',
            1: 'Enter the mysterious forest',
            2: 'Quit'
        }
        self.labels = dict()
        for i in range(3):
            self.labels[i] = ft.render(txt_labels[i], True, (11, 11, 55))

    # override
    def on_paint(self, ev):
        ev.screen.fill(self._bg_color)
        # draw labels
        for i, lbl in self.labels.items():
            p = self.optioncode_to_pos[i]
            ev.screen.blit(lbl, (p[0]+50, p[1]))
        # draw the "cursor"
        p = self.pos_cursor
        pygame.draw.rect(ev.screen, 'purple', (p[0], p[1], 44, 44))

    def on_select_menu_option(self, ev):
        self.pos_cursor = self.optioncode_to_pos[ev.option]


class MenuScreenCtrl(kengi.EvListener):
    def __init__(self, refmod):
        super().__init__()
        self._mod = refmod

    def on_quit(self, ev):
        self.pev(EngineEvTypes.Gameover)

    def on_keydown(self, ev):
        if ev.key == pygame.K_DOWN:
            self._mod.increm()
        elif ev.key == pygame.K_UP:
            self._mod.decrem()
        elif ev.key == pygame.K_RETURN or ev.key == pygame.K_KP_ENTER:
            if self._mod.curr_option == MiniModel.QUITOPTION:  # quit
                self.pev(EngineEvTypes.Gameover)
            elif self._mod.curr_option == MiniModel.FOREST:  # forest
                self.pev(EngineEvTypes.StatePush, state_ident=GameStates.ForestLevel)
            elif self._mod.curr_option == MiniModel.WORLD:  # explore world
                self.pev(EngineEvTypes.StatePush, state_ident=GameStates.Overworld)


class MiniModel(kengi.Emitter):
    WORLD = 0
    FOREST = 1
    QUITOPTION = 2

    def __init__(self):
        super().__init__()
        self.curr_option = self.WORLD
        self.total_nb_options = 3

    def increm(self):
        self.curr_option += 1
        if self.curr_option >= self.total_nb_options:
            self.curr_option = 0
        # info forwarding (->goal: auto- update the view)
        self.pev(MyEvTypes.SelectMenuOption, option=self.curr_option)

    def decrem(self):
        self.curr_option -= 1
        if self.curr_option < 0:
            self.curr_option = self.total_nb_options-1
        # info forwarding (->goal: auto- update the view)
        self.pev(MyEvTypes.SelectMenuOption, option=self.curr_option)


class MenuScreenState(BaseGameState):
    def __init__(self, gs_id):
        super().__init__(gs_id)
        self.v = self.c = None

    def enter(self):
        print('MenuScreenState ENTER')
        m = MiniModel()
        self.v = MenuScreenView(m.curr_option)
        self.v.turn_on()
        self.c = MenuScreenCtrl(m)
        self.c.turn_on()

    def release(self):
        print('MenuScreenState RELEASE')
        self.c.turn_off()
        self.c = None
        self.v.turn_off()
        self.v = None

    def pause(self):
        self.c.turn_off()
        self.v.turn_off()
        print('-->MenuScreen state was paused')

    def resume(self):
        self.v.turn_on()
        self.c.turn_on()
        print('-->MenuScreen state was resumed')
