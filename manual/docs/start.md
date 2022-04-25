# Creating games

## Basics in Pygame

The KataSDK includes the Kata Engine (`kataen` for short). This game engine is a wrapper around the Pygame library. You can tell wether a game is based on Pygame by checking wether it contains the `import pygame` line, or not.

If you don't know anything about Pygame yet, the first step would be to learn about it. You can Ctrl+click this link to browse the [official Pygame homepage](https://pygame.org), or check the nice [pygame documentation](https://www.pygame.org/docs/).

Once you get used to Pygame, and know how to use it, you can check this basic example:
```pygame
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

The kata Engine uses a similar, but slightly different approach for the creation of games.
We will use this same example an transform it to make it `kata`-compliant.

## Transition from Pygame to the Kata Engine

An important detail about the Kata Engine is that it is based on the MVC *design pattern*. MVC stands for Model-View-Controller. While it may seem complex first, it is really a straightforward pattern.

You can read more about it (Here)[https://www.geeksforgeeks.org/mvc-design-pattern/].

The previous program can be easily transformed using pre-defined the class `EventReceiver`. The game engines handles events automatically, so you don't really need to worry about it anymore!
For clarity, the new program is broken down in two parts:

### Part I. definitions

```pygame
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
```

### Part II. main program

```pygame
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

**Important remark:**
when using this SDK, you always need to create a `main.py` file that contains a `def run_game():` statement.
This becomes the entry point for the web version of your game!
Be aware that your game won't be able to run and will crash in the web context if you forget this rule!

## Kata engine main functions & classes

Functions:

+ `get_screen()`
+ `get_game_ctrl()`
+ `get_manager()`
+ `import_pygame()`

Classes or objects: 

+ `CogObject`
+ `EventReceiver`
+ `EngineEvTypes`
