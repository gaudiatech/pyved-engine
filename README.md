# Create 'magic' pygame-based games


A new tool suite that enables your games to be:
 
+ **standardized** - stop rewriting game building blocks over & over again. We've got you covered!

+ **structured** - use the integrated M-V-C architecture to reach a rare and amazing level of Code reuse;

+ **web compatible** - share your creations online with no hassle... It's finally here!


## Installation


To install the ready-to-use KataSDK locally, type:
`pip install katasdk`

You can start experimenting by adding this line in your source-code:
`import katagames_sdk.engine as kataen`


## Requirements and documentation

The Katagames Engine (`kataen` for short) is a wrapper around pygame therefore `pygame>=2.0.1` is required.

The KataSDK official documentation is available here:
[kata.games/developers](https://kata.games/developers).

These pages are built using the `mkdocs` tool. You can help improving the docs if you wish! All docs sources are located in the `docs/` folder of this repository. 


## Getting started guide


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

These programs are shared as `min-example-0.py` and `min-example-1.py` in the current repo.
The structural change comes from the fact that the Katagames Engine uses the MVC design pattern.
It also uses a game controller (an object that inherits from `EventReceiver` but also exposes a special `loop` method) in order to ensure compatibility with the Web context. Notice we have put our main code inside a `run_game()` function. This is also important when using `kataen`, if you wish to *bundle our game and effectively run it in a Web context!*

Refer to the official documentation for more info.


## About graphic modes


All games that are based upon `kataen` run in a fixed-size window of 960x540 pixels,
while this seems to be a problem it has many benefits for permance / web compatibility.

Moreover your effective in-game resolution can be selected amongst **three different possibilities**:

+ the HD_MODE: 960x540 pixels (no upscaling at all)
+ the OLD_SCHOOL_MODE: 480x270 (game screen is upscaled by 2)
+ the SUPER_RETRO_MODE: 320x180 (game screen is upscaled by 3)


## Repo content description


**The present repository contains:**
+ the Game Engine that is a component of the KataSDK, requires `pygame>=2.0.1`
+ the client-side API to communicate with [https://kata.games](https://kata.games) servers
+ sources for the official KataSDK documention

**Identify bugs, improve tools so everyone can benefit**
One of the main purpose for this repository is to allow people to list bugs/ crashes by submitting issues directly on github. If you've found a bug, please create an issue here and describe how to reproduce your bug.

**Long term goal of the KataSDK:**
"Code - test - publish - monetize your games using one single Tool Suite!"


## License


Materials in this repo are licensed under the LGPL3 license, see `LICENSE` file.

