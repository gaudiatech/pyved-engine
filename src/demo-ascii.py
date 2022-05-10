import katagames_engine as kengi


kengi.init('hd')

CAR_SIZE = 20  # 20, 16, 12, 10, 8 fonctionnent tous!
pygame = kengi.pygame

# - deprecated
# t_possib = list()
# for i in range(330, 1200):
#     if (i / 8 == i // 8) and (i / 12 == i // 12) and\
#             (i / 16 == i // 16) and (i / 10 == i // 10) and (i / 20 == i // 20):
#         t_possib.append(i)
# all_possib = list()
# for i in t_possib:
#     for j in t_possib:
#         if i > j:
#             all_possib.append((i, j, abs(1.61803398875 - j / i)))
# all_possib.sort(key=lambda t1: t1[2])
# for e in all_possib:
#     print(' {} x {} ratio {}'.format(*e))

# - const
IDX_CURSOR = 254
PAL = kengi.palettes.c64

asc_canvas = kengi.ascii.Acanvas()
canv_bsupx, canv_bsupy = asc_canvas.bounds

clock = pygame.time.Clock()
tpos = [0, 0]
text_pos = None
ajouts = dict()
gameover = False

while not gameover:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
            gameover = True
        elif ev.type == pygame.MOUSEBUTTONDOWN:
            text_pos = list(kengi.ascii.Acanvas.screen_to_cpos(ev.pos))
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

    asc_canvas.screen.fill(PAL['blue'])
    pp = pygame.mouse.get_pos()
    p = list(asc_canvas.screen_to_cpos(pp))

    # draw the tileset
    for i in range(256):
        tpos[0] = (i % 16)
        tpos[1] = (i // 16)
        asc_canvas.put_char(i, tpos, PAL['lightblue'])

    # draw palette
    cf = kengi.ascii.CODE_FILL
    for i in range(16):
        asc_canvas.put_char(cf, (i, 32), PAL[i])
        asc_canvas.put_char(cf, (i, 33), PAL[i])
        asc_canvas.put_char(cf, (i, 34), PAL[i])

    for adhoc_tpos, aj in ajouts.items():
        if len(aj):
            tmp = asc_canvas.alphabet.render(aj, PAL[3], PAL['darkgrey'])
            asc_canvas.paste(tmp, adhoc_tpos)

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

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
