"""
Game template: placeholder

joint work - tankking & wkta-tom

"""
import glvars
import random
import katagames_engine as kengi
kengi.bootstrap_e()

from myevents import MyEvTypes  # so we can post any custom(~homemade!) event in the Event Manager


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
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                self.pev(EngineEvType.GAMEENDS)


class Mob(GameObject):
    free_id = 1

    def __init__(self, pos):
        super().__init__()
        self.ident = Mob.free_id
        Mob.free_id += 1

        self.screen = kengi.get_surface()
        self.xsup, self.ysup = self.screen.get_size()

        self.x, self.y = pos

        self.dx = self.dy = 0
        self.alive = True

        # testing only
        self.phase = 0
        self.dx = 1  # TODO need to use float for coding the real thing, otherwise mobs go forward as if they lag
        self.dy = 3

    def proc_event(self, ev, source):
        if not self.alive:
            return

        if ev.type == EngineEvType.PAINT:
            pygame.draw.circle(self.screen, 'red', (self.x, self.y), 8)

        elif ev.type == EngineEvType.LOGICUPDATE:  # receives a special built-in event that is posted once per frame
            self.phase += 1

            if not(self.phase % 5):  # move only once per each 5 frame
                self.phase = 0

                self.x += self.dx
                self.y += self.dy
                if self.x >= self.xsup or self.y >= self.ysup:
                    self.alive = False
                    self.pev(MyEvTypes.MobDies, id=self.ident)


class Logger(GameObject):
    """
    just print stuff to the console, debug purpose
    """
    def proc_event(self, ev, source):
        if ev.type == MyEvTypes.MobDies:
            print(f'mob {ev.id} dies')


# - main program
def run_game():
    kengi.init('old_school', caption='tower defence', maxfps=30)

    # - set up stuff for using the event system (no ticker)
    gctrl = kengi.core.get_game_ctrl()
    gctrl.turn_on()

    # my game objects
    disp = MainDisplay()
    disp.turn_on()
    mobs = [Mob((96+random.randint(-29, 48), 8+random.randint(-3, 55))) for _ in range(8)]
    for m in mobs:
        m.dx += random.randint(1, 5)  # add randomness in how mobs move
        m.dy += random.randint(0, 4)  # add randomness in how mobs move
        m.turn_on()
    lo = Logger()
    lo.turn_on()

    # game loop
    gctrl.loop()

    kengi.quit()
    print('bye')


if __name__ == '__main__':
    run_game()
