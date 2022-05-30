"""
shows how one would implement multi-state games:
with kengi vs in pygame
see demo-b-pygame for comparison.
"""

import katagames_engine as kengi
kengi.init('old_school')
pygame = kengi.pygame
StackBasedGameCtrl = kengi.event.StackBasedGameCtrl
EngineEvTypes = kengi.event.EngineEvTypes
ReceiverObj = kengi.event.EventReceiver

# constants
BG_COLOR_ROOM1 = 'salmon'
BG_COLOR_ROOM2 = 'darkblue'
PL_COLOR = (105, 184, 251)
INIT_PL_POS = (240, 135)

# gamestates declaration
GameStates = kengi.struct.enum(
    'Room1',
    'Room2'
)


class Room1Manager(ReceiverObj):
    def __init__(self):
        super().__init__()
        self.pl_pos = [44, 77]
        self.fresh_st = True
        self.av_pos = list(INIT_PL_POS)
        self.scr_size = kengi.get_surface().get_size()

    def proc_event(self, ev, source):
        if ev.type == EngineEvTypes.LOGICUPDATE:
            self.av_pos[0] = (self.av_pos[0] - 2) % self.scr_size[0]
            self.av_pos[1] = (self.av_pos[1] + 1) % self.scr_size[1]

        elif ev.type == EngineEvTypes.PAINT:
            ev.screen.fill(BG_COLOR_ROOM1)
            pygame.draw.circle(
                ev.screen, PL_COLOR, self.av_pos, 15, 0
            )
            kengi.flip()

        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_RIGHT:
                self.fresh_st = False
                self.pev(EngineEvTypes.PUSHSTATE, state_ident=GameStates.Room2)
            elif ev.key == pygame.K_RETURN and not self.fresh_st:
                self.pev(EngineEvTypes.PUSHSTATE, state_ident=GameStates.Room2)
            elif ev.key == pygame.K_ESCAPE:
                self.pev(EngineEvTypes.GAMEENDS)


class Room1(kengi.BaseGameState):
    def __init__(self, stid):
        super().__init__(stid)
        self.saved_pos = [None, None]
        self.ctrl = None

    def enter(self):
        if self.ctrl is None:
            self.ctrl = Room1Manager()
        self.ctrl.turn_on()

    def pause(self):
        self.ctrl.turn_off()

    def resume(self):
        self.ctrl.turn_on()

    def release(self):
        self.ctrl.turn_off()
        self.ctrl = None


class Room2Manager(ReceiverObj):
    def __init__(self):
        super().__init__()
        self.av_pos = list(INIT_PL_POS)
        self.scr_size = kengi.get_surface().get_size()

    def proc_event(self, ev, source):
        if ev.type == EngineEvTypes.LOGICUPDATE:
            self.av_pos[0] = (self.av_pos[0] + 3) % self.scr_size[0]
            self.av_pos[1] = (self.av_pos[1] - 1) % self.scr_size[1]

        elif ev.type == EngineEvTypes.PAINT:
            ev.screen.fill(BG_COLOR_ROOM2)
            pygame.draw.circle(
                ev.screen, (PL_COLOR[2], PL_COLOR[0], PL_COLOR[1]), self.av_pos, 37, 0
            )
            kengi.flip()

        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_LEFT or ev.key == pygame.K_RETURN:
                print('pop state')
                self.pev(EngineEvTypes.POPSTATE)
            elif ev.key == pygame.K_ESCAPE:
                self.pev(EngineEvTypes.GAMEENDS)


class Room2(kengi.BaseGameState):
    def __init__(self, stid):
        super().__init__(stid)
        self.saved_pos = [None, None]
        self.ctrl = None

    def enter(self):
        self.ctrl = Room2Manager()
        self.ctrl.turn_on()

    def release(self):
        self.ctrl.turn_off()


def play_game():
    game_ctrl = StackBasedGameCtrl(
        kengi.get_game_ctrl(),
        GameStates,
        None,  # glvars
        {
            GameStates.Room1: Room1,
            GameStates.Room2: Room2
        }
    )
    game_ctrl.turn_on()
    game_ctrl.loop()


if __name__ == '__main__':
    print(" KENGI implem of ~~~ Demo B | controls:")
    print(" - RIGHT/LEFT arrow (change state)\n - ENTER (go back)\n - ESCAPE")
    print()
    print('press right first')
    pygame.init()
    pygame.display.set_caption('demo-b uses pygame only')
    play_game()
    pygame.quit()
    print('bye.')
