"""
Match3 game
Author: wkta-tom. Game template written for kengi
"""
import sys
sys.path.append("..\\..\\")
import katagames_engine as kengi
kengi.init()
EngineEvTypes = kengi.event.EngineEvTypes
CgmEvent = kengi.event.CgmEvent

from logic import Grid, C_EVIL, C_EMERALD, C_FIRESTONE, C_HEART, C_RUBY, C_STAR
from events import MyEvTypes


ICON_W, ICON_H = 60, 60
THR = 644


class PuzzleView(kengi.event.EventReceiver):
    def __init__(self):
        super().__init__()

    def proc_event(self, ev, source=None):
        if ev.type == EngineEvTypes.PAINT:
            # draw
            scr.fill('antiquewhite2')
            for gcoords, symcode in gamegrid:
                tmp_pos = map_c_to_screen(gcoords)
                if symcode is not None:  # otherwise we dont display anything
                    scr.blit(sym_to_img_table[symcode], tmp_pos)

            kengi.flip()
        elif ev.type == MyEvTypes.Explosion:
            print('explo @ '+str(ev.einfos))


def map_c_to_screen(gamcoords):
    return [20+68*gamcoords[0], 20+66*gamcoords[1]]


def test_snapgrid(mousecoords):
    for j in range(Grid.HEIGHT):
        for i in range(Grid.WIDTH):
            test_pt = map_c_to_screen((i, j))
            test_pt[0] += ICON_W//2
            test_pt[1] += ICON_H//2
            if (lambda u, v: (u[0] - v[0])**2 + (u[1] - v[1])**2)(mousecoords, test_pt) < THR:
                print(i, j)
                return i, j


def game_enter():
    global pygame, scr, gamegrid, sym_to_img_table, mger
    pygame = kengi.pygame  # important: one can bind pygame, but always after the .init() step!
    scr = kengi.core.get_screen()
    mger = kengi.event.EventManager.instance()

    # load assets
    sym_to_img_table[C_EVIL] = pygame.image.load('assets/tileBlack_31.png')
    sym_to_img_table[C_EMERALD] = pygame.image.load('assets/tileGreen_42.png')
    sym_to_img_table[C_FIRESTONE] = pygame.image.load('assets/tileOrange_27.png')

    sym_to_img_table[C_HEART] = pygame.image.load('assets/tilePink_36.png')
    sym_to_img_table[C_RUBY] = pygame.image.load('assets/tileRed_34.png')
    sym_to_img_table[C_STAR] = pygame.image.load('assets/tileYellow_33.png')
    for code, img in sym_to_img_table.items():  # normalize size
        sym_to_img_table[code] = pygame.transform.scale(img, (ICON_W, ICON_H))

    # init model
    gamegrid = Grid()


def game_update(tinfo=None):
    global gameover, gamegrid, sym_to_img_table, scr, mger, draggin
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            gameover = True
        elif ev.type == pygame.MOUSEBUTTONDOWN:
            draggin = test_snapgrid(ev.pos)

        elif ev.type == pygame.MOUSEBUTTONUP:
            temp = test_snapgrid(ev.pos)
            te = gamegrid.can_swap(draggin, temp)
            print('can swap? ', te)
            if draggin and temp and te:
                gamegrid.swap(draggin, test_snapgrid(ev.pos))
                draggin = None

        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_SPACE:
                pass

    mger.post(CgmEvent(EngineEvTypes.PAINT, screen=scr))
    mger.update()


def game_exit():
    kengi.quit()


# - glvars
sym_to_img_table = dict()
pview = PuzzleView()
pview.turn_on()
draggin = False
scr = gamegrid = mger = None
pygame = kengi.pygame
gameover = False


# - program body
if __name__ == '__main__':
    game_enter()
    while not gameover:
        game_update()
    game_exit()
