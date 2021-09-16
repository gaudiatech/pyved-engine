# KataSDK Python Package

Code - test - publish - monetize your games based on pygame, using one single Tool Suite!

## Installation

`pip install katasdk`

## Documentation

The KataSDK official documentation is to be found

Here: [kata.games/developers](https://kata.games/developers).

## Basic example: how to start using kataen

The Katagames Engine (or `kataen` for short) is a wrapper around pygame.

Imagine you have an existing game that you would like to transform/run on the web. 
Let us take one basic example that relies solely on the Pygame library:
```python
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
```

You would need to modify it a little bit but this process is fairly easy. The purpose of refactoring code is to simply plug your existing code to higher-level functions and objects, defined by `kataen`.
Here is how one would rewrite the same program:

```python
import katagames_sdk.engine as kataen
pygame = kataen.import_pygame()
EventReceiver = kataen.EventReceiver
EngineEvTypes = kataen.EngineEvTypes
scr_size=None

class Avatar:
  def __init__(self):
    self.pos = [240, 135]
    self.direct = 0

class AvatarView(EventReceiver):
  def __init__(self, avref):
    super().__init__()
    self.avref = avref
  def proc_event(self, ev, source):
    global scr_size
    if ev.type == EngineEvTypes.PAINT:
      ev.screen.fill(pygame.color.Color('antiquewhite2'))
      pygame.draw.circle(ev.screen, (244,105,251), self.avref.pos, 15, 0)

class AvatarCtrl(EventReceiver):
  def __init__(self, avref):
    super().__init__()
    self.avref = avref
  def proc_event(self, ev, source):
    global scr_size
    if ev.type == EngineEvTypes.LOGICUPDATE:
      avdir = self.avref.direct
      self.avref.pos[1] = (self.avref.pos[1] + avdir) % scr_size[1]
    elif ev.type == pygame.QUIT:
      gameover = True
    elif ev.type == pygame.KEYDOWN:
      if ev.key == pygame.K_UP:
        self.avref.direct = -1
      elif ev.key == pygame.K_DOWN:
        self.avref.direct = 1
    elif ev.type == pygame.KEYUP:
      prkeys = pygame.key.get_pressed()
      if not(prkeys[pygame.K_UP] or prkeys[pygame.K_DOWN]):
        self.avref.direct = 0

def run_game():
  global scr_size
  kataen.init(kataen.OLD_SCHOOL_MODE)
  scr_size = kataen.get_screen().get_size()
  av = Avatar()
  li_recv = [kataen.get_game_ctrl(), AvatarView(av), AvatarCtrl(av)]
  for recv_obj in li_recv:
    recv_obj.turn_on()
  li_recv[0].loop()
  kataen.cleanup()

if __name__=='__main__':
  run_game()
```

The structural change is due to the fact that the Katagames Engine uses the MVC design pattern. We also use a game controller (an object that inherits from `EventReceiver` but also exposes a special `loop` method) in order to ensure compatibility with the Web context.

You can also notice that we have put our main code inside a `run_game()` function. This is important when using `kataen`, as it will allow to *bundle our game and effectively run it in a Web context!*

## Graphic modes
All games that rely on the `kataen` component run in a fixed-size window of 960x540 pixels.

However, your effective in-game resolution can be selected amongst **three different possibilities**:

+ the SUPER_RETRO_MODE: 320x180 (game screen is upscaled by 3)
+ the OLD_SCHOOL_MODE: 480x270 (game screen is upscaled by 2)
+ the HD_MODE: 960x540 (without any upscaling)
