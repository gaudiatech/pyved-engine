import katagames_engine as kengi


SCR_W = 290
kengi.init(2)
screen = kengi.get_surface()
gameover = False
pygame = kengi.pygame
clock = pygame.time.Clock()
font = kengi.gfx.EmbeddedCfont()  # use default internal font
reg_font = pygame.font.Font(None, 20)


def draw_tiles():
    decal = 28
    for alpha in range(0, 17):
        yalign = 2 + 11 * alpha
        for k in range(alpha * decal, (alpha + 1) * decal):
            try:
                idx = 'tile{:03d}.png'.format(k)
                dest = ((k - alpha * decal) * 11, yalign)
                screen.blit(font.sheet[idx], dest)
            except KeyError:
                pass


def fill_cells(to_rank):
    for k in range(to_rank):
        i, j = k % 16, k // 16
        # swap i,j
        tmp = j
        j = i
        i = tmp

        scr_pos = (18 * i, 22 * j)
        pygame.draw.rect(screen, 'orange', (scr_pos[0] - 1, scr_pos[1] - 1, 18, 24))


def draw_cell(code):
    i, j = code % 16, code // 16
    # swap i,j
    tmp = j
    j = i
    i = tmp

    scr_pos = (18 * i, 22 * j)
    pygame.draw.rect(screen, 'antiquewhite3', (scr_pos[0] - 1, scr_pos[1] - 1, 18, 24), 1)

    txt = ' ' if (not code) else chr(code)
    surf = reg_font.render(txt, False, 'black')
    screen.blit(surf, (scr_pos[0]+1, scr_pos[1]))

    font.text_to_surf(txt, screen, (scr_pos[0], scr_pos[1] + 14), spacing=0)


# 1 : focus on the spr sheet cut process
# 2 : compare with a regular ttf font
mode = 1
fill = 1
# can set the flag to True if we need to dump ascii codes in the console
# ProtoFont.SPAM_CAR = True


while not gameover:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            gameover = True
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                gameover = True
            elif ev.key == pygame.K_SPACE:
                fill += 1
            elif ev.key == pygame.K_RETURN:
                print(fill-1)

    screen.fill('pink')

    if mode == 1:
        draw_tiles()
    elif mode == 2:
        # - tab comparatif
        fill_cells(fill)
        for i in range(0, 256):
            draw_cell(i)

    # --- affiche lettres en se basant sur leur code ascii
    # tmp = 180
    # xpos = 0
    # for k, asciicode in enumerate(range(32, 127)):
    #     screen.blit(
    #         font[chr(asciicode)],
    #         (xpos, tmp)
    #     )
    #     xpos += 10
    #     if xpos > SCR_W:
    #         xpos = 0
    #         tmp += 11

    # --- draw all caracters, no specific layout
    if mode == 1:
        m = ''
        for x in range(32, 82):
            m += chr(x)
        font.text_to_surf(m, screen, (8, 177 + 11 * 0), spacing=1, bgcolor='orange')
        m = ''
        for x in range(82, 132):
            m += chr(x)
        font.text_to_surf(m, screen, (8, 177 + 11 * 1), spacing=1, bgcolor='orange')
        m = ''
        for x in range(132, 182):
            m += chr(x)
        font.text_to_surf(m, screen, (8, 177 + 11 * 2), spacing=1, bgcolor='orange')
        m = ''
        for x in range(182, 232):
            m += chr(x)
        font.text_to_surf(m, screen, (8, 177 + 11 * 3), spacing=1, bgcolor='orange')
        m = ''
        for x in range(232, 256):
            m += chr(x)
        font.text_to_surf(m, screen, (8, 177 + 11 * 4), spacing=1, bgcolor='orange')

    # commit all gfx data
    kengi.flip()
    clock.tick(44)

print('clean exit')
