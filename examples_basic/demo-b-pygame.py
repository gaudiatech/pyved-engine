"""
shows how one would implement multi-state games:
in pygame vs with kengi
see demo-b-kengi for comparison.

A few weaknesses /drawbacks:
*  it is not easy to separate or distinguish
   data that should be linked to a particular state, fro global data.
   If room1 needs to remember the position after state exit,
   it's very easy to loose such information.

*  states are not labelled, having a large number of states makes the
   program less readable.
"""
import pygame


# constants
BG_COLOR_ROOM1 = 'salmon'
BG_COLOR_ROOM2 = 'darkblue'
PL_COLOR = (105, 184, 251)
SCR_SIZE = (640, 480)
MAXFPS = 25
INIT_PL_POS = (240, 135)


# ------------------------
#  states declaration
# -----------------------
class BaseState:
    def enter(self, gdata):  # we dont define this method static, for easier re-definition in subclasses
        raise NotImplementedError

    def update_func(self, gamedata, scr):
        pass


class Room1(BaseState):
    def __init__(self):
        self.saved_pos = [None, None]

    def enter(self, gdata):
        if self.saved_pos[0] is not None:
            gdata.av_pos[0], gdata.av_pos[1] = self.saved_pos

    def update_func(self, gamedata, scr):
        # copy
        self.saved_pos[0], self.saved_pos[1] = gamedata.av_pos[0], gamedata.av_pos[1]

        if event_handling(pygame.event.get(), gamedata):
            return

        gamedata.av_pos[0] = (gamedata.av_pos[0] - 2) % SCR_SIZE[0]
        gamedata.av_pos[1] = (gamedata.av_pos[1] + 1) % SCR_SIZE[1]

        scr.fill(BG_COLOR_ROOM1)
        pygame.draw.circle(scr, PL_COLOR, gamedata.av_pos, 15, 0)
        pygame.display.update()
        gamedata.clock.tick(MAXFPS)


class Room2(BaseState):
    def __init__(self):
        self.saved_pos = [None, None]

    def enter(self, gdata):
        if self.saved_pos[0] is None:
            gdata.av_pos[0], gdata.av_pos[1] = INIT_PL_POS
        else:
            gdata.av_pos[0], gdata.av_pos[1] = self.saved_pos

    def update_func(self, gamedata, scr):
        # cp
        self.saved_pos[0], self.saved_pos[1] = gamedata.av_pos[0], gamedata.av_pos[1]

        if event_handling(pygame.event.get(), gamedata):
            return

        gamedata.av_pos[0] = (gamedata.av_pos[0] + 3) % SCR_SIZE[0]
        gamedata.av_pos[1] = (gamedata.av_pos[1] - 1) % SCR_SIZE[1]

        scr.fill(BG_COLOR_ROOM2)
        pygame.draw.circle(scr, (PL_COLOR[2], PL_COLOR[0], PL_COLOR[1]), gamedata.av_pos, 37, 0)
        pygame.display.update()
        gamedata.clock.tick(MAXFPS)


def change_state(v, gdat):
    global prev_state, curr_state
    prev_state = curr_state
    curr_state = v
    states[curr_state].enter(gdat)  # with pygame, one needs to remember to do this manually


states = {
    0: Room1(),
    1: Room2()
}
prev_state = None
curr_state = 0


# ------------------------
#  generic/shared behavior
# -----------------------
class GameData:
    def __init__(self):
        self.game_over = False
        self.av_pos = list(INIT_PL_POS)
        self.clock = pygame.time.Clock()


def event_handling(ev_queue, gdata):
    global prev_state, curr_state
    for ev in ev_queue:
        if ev.type == pygame.QUIT:
            gdata.game_over = True
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                gdata.game_over = True

            elif ev.key == pygame.K_RETURN:
                if prev_state is not None:
                    change_state(prev_state, gdata)
                    return True
            if ev.key == pygame.K_RIGHT:
                if curr_state + 1 in states.keys():
                    change_state(curr_state + 1, gdata)
                    return True
            if ev.key == pygame.K_LEFT:
                if curr_state - 1 in states.keys():
                    change_state(curr_state - 1, gdata)
    return False


def play_game():
    global curr_state
    gamedata = GameData()
    screen = pygame.display.set_mode(SCR_SIZE)
    while not gamedata.game_over:
        states[curr_state].update_func(gamedata, screen)


if __name__ == '__main__':
    print("Demo B | controls:")
    print(" - RIGHT/LEFT arrow (change state)\n - ENTER (go back)\n - ESCAPE")
    pygame.init()
    pygame.display.set_caption('demo-b uses pygame only')
    play_game()
    pygame.quit()
    print('bye.')
