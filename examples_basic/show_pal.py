import katagames_engine as kengi
import math
kengi.bootstrap_e()


# const
START_POS = (16, 32)
BAR_LENGTH = 300
TILE_HEIGHT = 48

pygame = kengi.pygame


# - init
kengi.init('old_school', caption='kengi.palettes showcase')

gameover = False
cl = pygame.time.Clock()
rounding_type = round_func = lambda x: x
ft = pygame.font.Font(None, 25)

pos2tile = dict()
pos2label = dict()
pos2size = dict()

curr_offset_y = 0
for name, pal in kengi.pal.ALL_PALETTES.items():
    best_tile_size = (BAR_LENGTH-pal.size+1) / pal.size
    t = BAR_LENGTH
    curr_offset_x = 0
    last_keyy = 0

    for d, col in enumerate(pal.listing):
        y = math.ceil(best_tile_size)
        tile_size = y if (y < t) else t
        t -= tile_size

        last_keyy = keyy = (d + START_POS[0] + curr_offset_x, START_POS[1] + curr_offset_y)
        tile_obj = pygame.Surface((tile_size, 8))
        tile_obj.fill(col)
        pos2tile[keyy] = tile_obj

        curr_offset_x += tile_size

    pos2label[(last_keyy[0]+24, last_keyy[1]+10)] = ft.render(name, False, (0, 0, 0))  # save a label
    pos2size[(last_keyy[0]+30, last_keyy[1] + 22)] = ft.render(f'size #{pal.size}', False, (88, 88, 100))  # another lbl

    curr_offset_y += TILE_HEIGHT

print('-- util. methods tests --')

n = 7
print(f'pick any color {n} times (japan pal)')
for _ in range(n):
    rcolor = kengi.pal.japan.at_random()
    print(rcolor, kengi.pal.japan.get_name(rcolor))
print()
n = 10
print(f'pick a color {n} times, but no black or white or violet')
for _ in range(n):
    rcolor = kengi.pal.c64.at_random(excl_set={'black', 'white', 'violet'})
    print(rcolor, kengi.pal.c64.get_name(rcolor))
n = 10
print(f'pick a color {n} times, but not 3 or 8 or 9 or 10')
for _ in range(n):
    rcolor = kengi.pal.c64.at_random(excl_set={3, 8, 9, 10})
    print(rcolor, kengi.pal.c64.get_rank(rcolor))


# - main program
def run_game():
    global gameover
    scr = kengi.get_surface()

    while not gameover:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                gameover = True
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    gameover = True
        # display
        scr.fill((0, 0, 255))

        for p, slabel in pos2size.items():
            scr.blit(slabel, p)
        for p, label in pos2label.items():
            scr.blit(label, p)
        for p, tile in pos2tile.items():
            scr.blit(tile, p)

        kengi.flip()
        cl.tick(60)

    kengi.quit()
    print('bye')


if __name__ == '__main__':
    run_game()
