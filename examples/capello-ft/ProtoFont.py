import katagames_engine as kengi
from collections import defaultdict

SCR_W = 290

kengi.init(2)
screen = kengi.get_surface()
gameover = False
pygame = kengi.pygame
clock = pygame.time.Clock()


class ProtoFont:
    UNKNOWN_CAR_RK = 123
    SPAM_CAR = False

    def __init__(self):
        # regular:
        # sprsheet = kengi.gfx.JsonBasedSprSheet('capello-ft')

        self._sheet = kengi.gfx.JsonBasedSprSheet('capello-ft', ck=(127, 127, 127))  #g_sprsheet

        # specific to capello-ft.png and capello-ft.json...
        # it maps ascii codes to the rank font000.png where 000 is the rank
        mappingtable = {
            174: 150,  #  (r)
            175: 151,
        }
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
        # upside-down !, cent ¢ , then £ symbol ... etc.
        for e in range(160, 173):
            mappingtable[e] = e - 24

        # caractère degré celsuis °
        for e in range(186, 186+16):
            mappingtable[e] = e - 33
        for e in range(192, 208):
            mappingtable[e] = e - 22
        # Ð 208
        for e in range(208, 224):
            mappingtable[e] = e - 21
        for e in range(224, 240):
            mappingtable[e] = e - 20
        self.car_height = defaultdict(lambda: 7)
        # for my_asciicode in range(*alphabet_span):
        #     self.car_height[chr(my_asciicode)] = 7  # CONST

        # - generic
        self.ascii2img = dict()
        defaultw = self._sheet['tile{:03d}.png'.format(self.UNKNOWN_CAR_RK)].get_width()
        self.car_width = defaultdict(lambda: defaultw)

        for my_asciicode in mappingtable.keys():
            ssurf = self._sheet['tile{:03d}.png'.format(mappingtable[my_asciicode])]
            self.ascii2img[my_asciicode] = ssurf
            self.car_width[chr(my_asciicode)] = ssurf.get_width()

    @property
    def sheet(self):
        return self._sheet

    def __getitem__(self, itemk):
        ascii_tmp = ord(itemk)
        if self.SPAM_CAR:
            print(itemk, ascii_tmp)
        try:
            return self.ascii2img[ascii_tmp]
        except KeyError:
            return self._sheet['tile{:03d}.png'.format(self.UNKNOWN_CAR_RK)]

    def text_to_surf(self, w, refsurf, start_pos, spacing=0, bgcolor=None):
        # fill background with a solid color, if requested
        if bgcolor:
            curr_pos = list(start_pos)
            h = float('-inf')
            for letter in w:
                curr_pos[0] += self.car_width[letter] + spacing
                if self.car_height[letter] > h:
                    h = self.car_height[letter]
            pygame.draw.rect(refsurf, bgcolor, (start_pos[0], start_pos[1], curr_pos[0]-spacing-start_pos[0], h), 0)
        # draw the text
        curr_pos = list(start_pos)
        for letter in w:
            refsurf.blit(self[letter], curr_pos)
            curr_pos[0] += self.car_width[letter] + spacing

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
