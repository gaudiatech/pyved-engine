
import katagames_engine as kengi
kengi.bootstrap_e()

# - aliases
pygame = kengi.pygame
tmx = kengi.tmx.misc
tmxdata = kengi.tmx.data

#SCR_SIZE = (640, 480)
OFFSET = 5
dj, di = 0, 0  # variation
stop_the_test = False

kengi.init(2)

clock = pygame.time.Clock()
#scr = pygame.display.set_mode(SCR_SIZE)
scr=kengi.core.get_screen()
scr_size = scr.get_size()

tm_obj = tmxdata.load_tmx('level.tmx')

# - debug infos
print(tm_obj.layers['set'], tm_obj.layers['triggers'])

print('------ testing TMX loading, TMX-based display ------')
print('use arrow keys to move viewport')

# init viewport
viewport = tmx.Viewport(tm_obj, (0, 0), scr_size)
viewport.force_focus(288, 240)

i, j = viewport.center  # since viewport was auto. init by constructor
print('initial i j values= ', i, j)

bg = None
if tm_obj.background:
    print('bg found')

    # turn background image to a sprite, so we can repeat it easily
    bg = pygame.sprite.Sprite()
    bg.image = pygame.image.load(tm_obj.background['img_path'])
    bg.rect = bg.image.get_rect()

    bg.rect.left = -16 + tm_obj.background['offsetx']
    bg.rect.top = 0
    print(bg.rect.topleft)

while not stop_the_test:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            stop_the_test = True
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_LEFT:
                di = -OFFSET
            elif ev.key == pygame.K_RIGHT:
                di = +OFFSET
            elif ev.key == pygame.K_DOWN:
                dj = +OFFSET
            elif ev.key == pygame.K_UP:
                dj = -OFFSET
        elif ev.type == pygame.KEYUP:
            pkeys = pygame.key.get_pressed()
            if (not pkeys[pygame.K_DOWN]) and (not pkeys[pygame.K_UP]):
                dj = 0
            if (not pkeys[pygame.K_LEFT]) and (not pkeys[pygame.K_RIGHT]):
                di = 0

    if dj != 0 or di != 0:
        i += di
        j += dj
        viewport.set_focus(i, j)
        i, j = viewport.center
        #viewport.force_focus(i, j)

    # manually blit the bg ...
    # scr.fill((0, 0, 0))
    scr.blit(bg.image, bg.rect.topleft)

    viewport.draw(scr)
    # pygame.display.flip()
    kengi.flip()
    clock.tick(50)

print('bye!')
kengi.quit()
