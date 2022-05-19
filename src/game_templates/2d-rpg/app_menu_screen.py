import katagames_engine as kengi
from myrpg_defs import GameStates, MyEvTypes


BaseGameState = kengi.BaseGameState
EventReceiver = kengi.event.EventReceiver
EngineEvTypes = kengi.event.EngineEvTypes
pygame = kengi.pygame


class MenuScreenView(EventReceiver):

    def __init__(self, selected_option):
        super().__init__(self)
        self._bg_color = 'antiquewhite3'

        self.optioncode_to_pos = {
            0: (33, 100),
            1: (33, 180),
            2: (33, 260)
        }
        self.pos_cursor = self.optioncode_to_pos[selected_option]

        ft = pygame.font.Font(None, 19)
        txt_labels = {
            0: 'Explore the world',
            1: 'Enter the dungeon',
            2: 'Quit'
        }
        self.labels = dict()
        for i in range(3):
            self.labels[i] = ft.render(txt_labels[i], True, (11, 11, 55))

    # override
    def proc_event(self, ev, source=None):
        if ev.type == EngineEvTypes.PAINT:
            ev.screen.fill(self._bg_color)

            # draw labels
            for i, lbl in self.labels.items():
                p = self.optioncode_to_pos[i]
                ev.screen.blit(lbl, (p[0]+50, p[1]))

            # draw the "cursor"
            p = self.pos_cursor
            pygame.draw.rect(ev.screen, 'purple', (p[0], p[1], 44, 44))

        elif ev.type == MyEvTypes.MenuOptionSelection:
            self.pos_cursor = self.optioncode_to_pos[ev.option]


class MenuScreenCtrl(EventReceiver):

    def __init__(self, refmod):
        super().__init__()
        self._mod = refmod

    # override
    def proc_event(self, ev, source=None):
        if ev.type == pygame.QUIT:
            self.pev(EngineEvTypes.GAMEENDS)

        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_DOWN:
                self._mod.increm()
            elif ev.key == pygame.K_UP:
                self._mod.decrem()
            elif ev.key == pygame.K_RETURN or ev.key == pygame.K_KP_ENTER:
                if self._mod.curr_option == 2:  # quit
                    self.pev(EngineEvTypes.GAMEENDS)
                elif self._mod.curr_option == 1:  # dungeon
                    pass
                elif self._mod.curr_option == 0:  # explore world
                    self.pev(EngineEvTypes.PUSHSTATE, state_ident=GameStates.Overworld)


class MiniModel(kengi.event.CogObj):
    def __init__(self):
        self.curr_option = 0
        self.total_nb_options = 3

    def increm(self):
        self.curr_option += 1
        if self.curr_option >= self.total_nb_options:
            self.curr_option = 0
        # info forwarding (->goal: auto- update the view)
        self.pev(MyEvTypes.MenuOptionSelection, option=self.curr_option)

    def decrem(self):
        self.curr_option -= 1
        if self.curr_option < 0:
            self.curr_option = self.total_nb_options-1
        # info forwarding (->goal: auto- update the view)
        self.pev(MyEvTypes.MenuOptionSelection, option=self.curr_option)


class MenuScreenState(BaseGameState):
    def __init__(self, gs_id, name):
        super().__init__(gs_id, name)
        self.v = self.c = None

    def enter(self):
        print('entering MenuScreen state...')
        m = MiniModel()
        self.v = MenuScreenView(m.curr_option)
        self.v.turn_on()
        self.c = MenuScreenCtrl(m)
        self.c.turn_on()

    def release(self):
        print('RELEASING MenuScreenState !')
        self.c.turn_off()
        self.c = None
        self.v.turn_off()
        self.v = None

    # override
    def pause(self):
        print('MenuScreen state is paused.')
        self.c.turn_off()
        self.v.turn_off()

    # override
    def resume(self):
        print('MenuScreen state is resumed.')
        self.v.turn_on()
        self.c.turn_on()
