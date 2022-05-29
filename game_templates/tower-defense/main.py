"""
Game template: placeholder

joint work - tankking & wkta-tom

"""
import glvars
import katagames_engine as kengi
kengi.bootstrap_e()


# let's use the event manager! game object can receive or send events
GameObject = kengi.event.EventReceiver
EngineEvType = kengi.event.EngineEvTypes
pygame = kengi.pygame


class MainDisplay(GameObject):
    def proc_event(self, ev, source):
        if ev.type == EngineEvType.PAINT:
            ev.screen.fill('orange')
        elif ev.type == EngineEvType.LOGICUPDATE:  # receives a special built-in event that is posted once per frame
            pass
        elif ev.type == pygame.QUIT:
            self.pev(EngineEvType.GAMEENDS)  # posts a special built-in event that stops the game ctrl loop


class Mob(GameObject):
    def __init__(self):
        super().__init__()
        self.screen = kengi.get_surface()
        self.x = self.y = 0

    def proc_event(self, ev, source):
        if ev.type == EngineEvType.PAINT:
            pygame.draw.circle(self.screen, 'orange', (self.x, self.y), 15)


# - main program
def run_game():
    kengi.init('old_school', caption='tower defence', maxfps=30)

    # - set up stuff for using the event system (no ticker)
    gctrl = kengi.core.get_game_ctrl()
    gctrl.turn_on()

    # my game objects
    disp = MainDisplay()
    disp.turn_on()
    mobs = [Mob() for _ in range(8)]
    for m in mobs:
        m.turn_on()

    # game loop
    gctrl.loop()

    kengi.quit()
    print('bye')


if __name__ == '__main__':
    run_game()
