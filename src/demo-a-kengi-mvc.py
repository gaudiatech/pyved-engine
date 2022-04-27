import katagames_engine as kengi
kengi.init('old_school', caption='demo-a KENGI-based, variant= mvc')
pygame = kengi.pygame
EngineEvTypes = kengi.event.EngineEvTypes


# declaring custom game events that are compatible with the kengi event-system:
MyEvents = kengi.event.enum_ev_types(
    'PlayerMoves',  # contains attributes x, y
    'PlayerColorChanges',  # contains color_code
)


# ------------------
#  this software variant produces the same result as any demo-a,
#  but it uses the M.V.C. pattern cf. the 3 classes below
# -----------------
class GameState(kengi.event.CogObj):
    # As a rule of thumb: all classes that model some aspect of your software should inherit from CogObj
    """
    the model
    """
    def __init__(self):
        super().__init__()
        self.av_pos = [240, 135]
        self.av_y_speed = 0
        self.curr_color_code = 0
        self.bounds = kengi.get_surface().get_size()

    def refresh_avatar_pos(self):
        self.av_pos[1] = (self.av_pos[1] + self.av_y_speed) % self.bounds[1]
        # dispatch info
        self.pev(MyEvents.PlayerMoves, x=self.av_pos[0], y=self.av_pos[1])

    def switch_avatar_color(self):
        self.curr_color_code = (self.curr_color_code + 1) % 2
        self.pev(MyEvents.PlayerColorChanges, color_code=self.curr_color_code)


class GameView(kengi.event.EventReceiver):
    """
    the view
    """
    BG_COLOR = 'antiquewhite2'

    def __init__(self, gs):
        super().__init__()
        self._col_palette = {
            0: (244, 105, 251),
            1: (105, 184, 251)
        }
        self.pl_screen_pos = list(gs.av_pos)
        self.pl_color = self._col_palette[gs.curr_color_code]

    def proc_event(self, ev, source):
        if ev.type == EngineEvTypes.PAINT:
            ev.screen.fill(self.BG_COLOR)
            pygame.draw.circle(ev.screen, self.pl_color, self.pl_screen_pos, 15, 0)
            kengi.flip()

        elif ev.type == MyEvents.PlayerMoves:
            self.pl_screen_pos[:] = [ev.x, ev.y]

        elif ev.type == MyEvents.PlayerColorChanges:
            self.pl_color = self._col_palette[ev.color_code]


class DemoCtrl(kengi.event.EventReceiver):
    """
    the controller
    """
    def __init__(self, gs):
        super().__init__()
        self.state = gs

    def proc_event(self, ev, source=None):
        if ev.type == kengi.event.EngineEvTypes.LOGICUPDATE:
            self.state.refresh_avatar_pos()

        elif ev.type == pygame.QUIT:
            kengi.core.get_game_ctrl().halt()

        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                kengi.core.get_game_ctrl().halt()
            elif ev.key == pygame.K_SPACE:
                self.state.switch_avatar_color()
            elif ev.key == pygame.K_UP:
                self.state.av_y_speed = -1
            elif ev.key == pygame.K_DOWN:
                self.state.av_y_speed = 1

        elif ev.type == pygame.KEYUP:
            prkeys = pygame.key.get_pressed()
            if (not prkeys[pygame.K_UP]) and (not prkeys[pygame.K_DOWN]):
                self.state.av_y_speed = 0


def play_game():
    """
    using the built-in event manager + game controller to execute the game
    """
    game_st = GameState()
    game_ctrl = kengi.core.get_game_ctrl()
    receivers = [game_ctrl, DemoCtrl(game_st), GameView(game_st)]
    for r in receivers:
        r.turn_on()  # listen to incoming events
    game_ctrl.loop()  # standard game loop


if __name__ == '__main__':
    print("mvc variant of ~~~ Demo A | controls:")
    print("UP/DOWN arrow, SPACE, ESCAPE")
    play_game()
    kengi.quit()
    print('bye.')
