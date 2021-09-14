import pygame
from pygame.locals import QUIT, KEYDOWN, KEYUP, K_UP, K_DOWN
scr_size = (480, 270)
avpos = [240, 135]
avdir = 0
gameover = False
clock = pygame.time.Clock()
pygame.init()
screen = pygame.display.set_mode(scr_size)
while not gameover:
  for ev in pygame.event.get():
    if ev.type == QUIT:
      gameover = True
    elif ev.type == KEYDOWN:
      if ev.key == K_UP:
        avdir = -1
      elif ev.key == K_DOWN:
        avdir = 1
    elif ev.type == KEYUP:
      prkeys = pygame.key.get_pressed()
      if not(prkeys[pygame.K_UP] or prkeys[pygame.K_DOWN]):
        avdir = 0
  # update logic, draw
  avpos[1] = (avpos[1] + avdir) % scr_size[1]
  screen.fill(pygame.color.Color('antiquewhite2'))
  pygame.draw.circle(screen, (244,105,251), avpos, 15, 0)
  pygame.display.flip()
  clock.tick(60)
pygame.quit()
print('game over.')
