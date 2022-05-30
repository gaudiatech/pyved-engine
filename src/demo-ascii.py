import katagames_engine as kengi
kengi.bootstrap_e()


# - const
CAR_SIZE = 20  # 20, 16, 12, 10, 8 fonctionnent tous!
IDX_CURSOR = 254
MAXFPS = 50
PAL = kengi.pal.c64


# - variables
pygame = kengi.pygame
ajouts = dict()
asc_canvas = kengi.ascii
canv_bsupx, canv_bsupy = asc_canvas.get_bounds()
clock = pygame.time.Clock()
gameover = False
text_pos = None
tpos = [0, 0]


# -- main program
kengi.init('hd')
_scr = kengi.core.get_screen()
asc_canvas.init()

while not gameover:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
            gameover = True
        elif ev.type == pygame.MOUSEBUTTONDOWN:
            text_pos = list(kengi.ascii.screen_to_cpos(ev.pos))
        elif ev.type == pygame.KEYDOWN:

            if ev.key == pygame.K_BACKSPACE:
                kengi.ascii.increm_char_size()
                text_pos = None

            elif (text_pos is not None) and ev.key != pygame.K_RETURN:
                cle = tuple(text_pos)
                if cle not in ajouts:
                    ajouts[cle] = list()
                if len(ev.unicode) == 1:
                    ajouts[cle].append(ev.unicode)

    _scr.fill(PAL['blue'])
    pp = pygame.mouse.get_pos()
    p = list(asc_canvas.screen_to_cpos(pp))

    # draw the tileset
    for i in range(ord('0'), ord('Z')):
        tpos[0] = (i % 16)
        tpos[1] = (i // 16)
        asc_canvas.put_char(chr(i), tpos, PAL['lightblue'])

    # draw palette
    cf = kengi.ascii.CODE_FILL
    for i in range(16):
        asc_canvas.put_char(cf, (i, 32), PAL[i])
        asc_canvas.put_char(cf, (i, 33), PAL[i])
        asc_canvas.put_char(cf, (i, 34), PAL[i])

    for adhoc_tpos, aj in ajouts.items():
        if len(aj):
            tmp_pos = list(adhoc_tpos)
            for e in list(aj):  # letter one by one
                tmp = asc_canvas.put_char(e, tmp_pos, PAL[3], PAL['darkgrey'])
                tmp_pos[0] += 1

    # draw the cursor
    gvpos = [
        (p[0] - 1, p[1] - 1),
        (p[0] + 1, p[1] - 1),
        (p[0] - 1, p[1] + 1),
        (p[0] + 1, p[1] + 1),
    ]
    for elt in ((True, gvpos[0]), (True, gvpos[-1]), (False, gvpos[1]), (False, gvpos[2])):
        flag, popo = elt
        car = '\\' if flag else '/'
        if asc_canvas.is_inside(popo):
            asc_canvas.put_char(car, popo, (250, 11, 33))

    kengi.flip()
    clock.tick(MAXFPS)

kengi.quit()
