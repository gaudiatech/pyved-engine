import random
from ... import _hub as inj
# import pygame


pygame = inj.pygame


class Label(pygame.sprite.Sprite):

    def __init__(self, txt, color=None):
        self._font = pygame.font.Font(None, 35)

        super().__init__()

        self._txt = txt

        self._color = None
        if color is None:
            color = (0, 0, 0)
        self.color = color

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        self.image = self._font.render(self._txt, False, value)
        self.rect = self.image.get_rect()


if __name__ == '__main__':
    pygame.init()
    scr = pygame.display.set_mode((400, 300))
    gameover = False
    cl = pygame.time.Clock()
    central_obj = Label('salut', 'steelblue')

    while not gameover:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                gameover = True
            elif ev.type == pygame.KEYDOWN:
                central_obj.color = random.choice(('orange', 'pink', 'yellow'))

            scr.fill((87, 77, 15))
            scr.blit(central_obj.image, central_obj.rect.topleft)
            pygame.display.update()
            cl.tick(60)
    print('test over.')
    pygame.quit()
