
import katagames_engine as kengi


kengi.init(3)
screen = kengi.get_surface()
gameover = False
pygame = kengi.pygame
clock = pygame.time.Clock()
sprsheet = kengi.gfx.JsonBasedSprSheet('capello-ft')


def draw_tiles():
    decal = 28
    for alpha in range(0, 17):
        yalign = 2+11*alpha
        for k in range(alpha*decal, (alpha+1)*decal):
            try:
                idx = 'tile{:03d}.png'.format(k)
                dest = ((k-alpha*decal)*11, yalign)
                screen.blit(sprsheet[idx], dest)
            except KeyError:
                pass


SCR_W = 290


class ProtoFont:

    UNKNOWN_CAR_RK = 123

    def __init__(self, g_sprsheet):
        self._sheet = g_sprsheet

        # specific to capello-ft.png and capello-ft.json...
        # it maps ascii codes to the rank font000.png where 000 is the rank
        mappingtable = dict()
        for e in range(32, 48):
            mappingtable[e] = e - 32
        for e in range(48, 64):
            mappingtable[e] = e - 31
        for e in range(64, 80):
            mappingtable[e] = e - 30
        for e in range(80, 96):
            mappingtable[e] = e - 29
        for e in range(96, 112):
            mappingtable[e] = e - 28
        for e in range(112, 127):
            mappingtable[e] = e - 27
        self.car_height = dict()
        alphabet_span = (32, 127)
        for my_asciicode in range(*alphabet_span):
            self.car_height[chr(my_asciicode)] = 7  # CONST

        # - generic
        self.ascii2img = dict()
        self.car_width = dict()
        for my_asciicode in range(*alphabet_span):
            ssurf = g_sprsheet['tile{:03d}.png'.format(mappingtable[my_asciicode])]
            self.ascii2img[my_asciicode] = ssurf
            self.car_width[chr(my_asciicode)] = ssurf.get_width()

    def __getitem__(self, itemk):
        return self.ascii2img[ord(itemk)]

    def text_to_surf(self, w, refsurf, start_pos):
        curr_pos = list(start_pos)
        for letter in w:
            refsurf.blit(self[letter], curr_pos)
            curr_pos[0] += self.car_width[letter]

    # def text_to_surf(self, w, refsurf, start_pos):
    #     curr_pos = list(start_pos)
    #     for letter in w:
    #         safecode = self.to_safe_code(ord(letter))
    #         print('traite: ',letter, ' safecode = ', safecode)
    #
    #         img = self._sheet['tile{:03d}.png'.format(safecode)]
    #         refsurf.blit(img, curr_pos)
    #         curr_pos[0] += self.car_width[safecode]
    #
    # def to_safe_code(self, a_code):
    #     try:
    #         gletter = chr(a_code)
    #         tmp = self[gletter]
    #         return a_code
    #     except (ValueError, KeyError):
    #         return self.UNKNOWN_CAR_RK


font = ProtoFont(sprsheet)


while not gameover:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            gameover = True
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                gameover = True

    screen.fill('pink')
    draw_tiles()

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

    # --- essai protofont text_to_surf
    font.text_to_surf('salut bro! ', screen, (8, 177))

    # commit gfx data
    kengi.flip()
    clock.tick(44)

print('clean exit')
