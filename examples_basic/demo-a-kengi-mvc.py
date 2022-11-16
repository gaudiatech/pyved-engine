import katagames_engine as kengi
from katagames_engine.default_backend import PygameKenBackend


kengi.init(2, caption='demo-a uses kengi / events+mvc variant')
pygame = kengi.pygame

ev2 = kengi.event2
EngineEvTypes = ev2.EngineEvTypes
gameover = False


# declaring custom game events that are compatible with the kengi event-system:
MyEvents = ev2.game_events_enum((
    'PlayerMovement',  # contains attributes x, y
    'ColorChange',  # contains color_code
))


# ------------------
#  this software variant produces the same result as any demo-a,
#  but it uses the M.V.C. pattern cf. the 3 classes below
# -----------------
class GameState(ev2.Emitter):
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
        self.pev(MyEvents.PlayerMovement, x=self.av_pos[0], y=self.av_pos[1])

    def switch_avatar_color(self):
        self.curr_color_code = (self.curr_color_code + 1) % 2
        self.pev(MyEvents.ColorChange, color_code=self.curr_color_code)


class GameView(ev2.EvListener):
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

    def on_player_movement(self, ev):
        self.pl_screen_pos[:] = [ev.x, ev.y]

    def on_color_change(self, ev):
        self.pl_color = self._col_palette[ev.color_code]

    def on_paint(self, ev):
        screen = kengi.get_surface()
        screen.fill(self.BG_COLOR)
        pygame.draw.circle(ev.screen, self.pl_color, self.pl_screen_pos, 15, 0)


class DemoCtrl(ev2.EvListener):
    """
    the controller
    """
    def __init__(self, gs):
        super().__init__()
        self.state = gs

    # def proc_event(self, ev, source=None):
    #
    #     if ev.type == pygame.KEYUP:


    def on_update(self, ev):
        self.state.refresh_avatar_pos()

    def on_quit(self, ev):
        global gameover
        gameover = True

    def on_keyup(self, ev):
        prkeys = pygame.key.get_pressed()
        if (not prkeys[pygame.K_UP]) and (not prkeys[pygame.K_DOWN]):
            self.state.av_y_speed = 0

    def on_keydown(self, ev):
        global gameover
        if ev.key == pygame.K_ESCAPE:
            gameover = True
        elif ev.key == pygame.K_SPACE:
            self.state.switch_avatar_color()
        elif ev.key == pygame.K_UP:
            self.state.av_y_speed = -1
        elif ev.key == pygame.K_DOWN:
            self.state.av_y_speed = 1


class MyGameCtrl(ev2.EvListener):
    MAXFPS = 75

    def __init__(self):
        super().__init__()
        self._clock = pygame.time.Clock()

    def loop(self):
        global gameover
        while not gameover:
            self.pev(ev2.EngineEvTypes.Update)
            self.pev(ev2.EngineEvTypes.Paint, screen=kengi.get_surface())
            self._manager.update()
            kengi.flip()
            self._clock.tick(self.MAXFPS)

        print('done!')


def play_game():
    """
    using the built-in event manager + game controller to execute the game
    """
    game_st = GameState()
    game_ctrl = MyGameCtrl()
    receivers = [game_ctrl, DemoCtrl(game_st), GameView(game_st)]
    # init! new event system!!
    ev2.EvManager.instance().setup(PygameKenBackend(), MyEvents)

    for r in receivers:
        r.turn_on()  # listen to incoming events
    game_ctrl.loop()  # standard game loop


if __name__ == '__main__':
    print(" KENGI events+mvc variant of ~~~ Demo A | controls:")
    print("UP/DOWN arrow, SPACE, ESCAPE")
    play_game()
    kengi.quit()
    print('bye.')
