from . import pimodules


pyv = pimodules.pyved_engine
pyv.bootstrap_e()
pyg = pyv.pygame
screen = None
r4 = pyg.Rect(32, 32, 128, 128)
kpressed = set()


@pyv.declare_begin
def init_game(vmst=None):
    global screen
    pyv.init(wcaption='Untitled pyved-based Game')
    screen = pyv.get_surface()


@pyv.declare_update
def upd(time_info=None):
    for ev in pyg.event.get():
        if ev.type == pyg.QUIT:
            pyv.vars.gameover = True
        elif ev.type == pyg.KEYDOWN:
            kpressed.add(ev.key)
        elif ev.type == pyg.KEYUP:
            kpressed.remove(ev.key)

    screen.fill('paleturquoise3')
    if len(kpressed):
        pyv.draw_rect(screen, 'orange', r4)
    pyv.flip()


@pyv.declare_end
def done(vmst=None):
    pyv.close_game()
    print('gameover!')
