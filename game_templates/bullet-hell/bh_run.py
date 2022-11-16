"""
Game template - Bullet Hell

Assets created by Dyru, license CC BY 4.0, https://www.instagram.com/art_by_dyru/
"""
import bh_glvars as glvars
import katagames_engine as kengi
from compo import MyView


manager = None
EngineEvTypes = kengi.event2.EngineEvTypes
myv = None
PygBackend = kengi.PygameKenBackend


def entergame(x=None):
    global manager, myv
    kengi.init(2, 'bullet hell game template')  # upscaling x2

    # to use events new ver
    manager = kengi.event2.EvManager.instance()
    manager.setup(PygBackend(), None)
    myv = MyView()
    myv.turn_on()


def updategame(dt):
    manager.post(EngineEvTypes.Update)
    manager.post(EngineEvTypes.Paint, screen=kengi.get_surface())
    manager.update()
    kengi.flip()


def exitgame(x=None):
    myv.turn_off()
    kengi.quit()


if __name__ == '__main__':
    entergame()
    while not glvars.gameover:
        updategame(0)
    exitgame()
    print('done.')
