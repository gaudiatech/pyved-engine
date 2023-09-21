# ECS in code

Here we will explain to you in further details how we implement ECS with the pyved engine.

## Syntax

Let's explain the syntax to code some of the basic code needed for ECS implementation.

### Entities

```py
    pyv.new_entity(composant1=X, composant2=Y)
```
This is the basic implementation of a new entity in pyved.

Let's see a real implementation examples in order to show some more possibilities :

```py
    pyv.new_entity(
        archetype='player',
        speed=0.0,
        controls={'left': False, 'right': False},
        body=pygame.rect.Rect(shared.SCR_WIDTH // 2, 635, shared.PL_WIDTH, shared.PL_HEIGHT)
    )
```

Here for example we specify an archetype for the player (This is explained a bit further, but it is not mandatory), and then some components, such as the player speed, the controls, and the hitbox.

You call these functions at the initialisation of your game.

### Components

As shown before, the components are part of an entity, the components can be pretty much everything.
It's a characteristic of an entity, could be speed, hit points, position and so much more...

You can call your entities by their components with 
```
pyv.find_by_components('yourComponent')
```

### Systems

The systems hosts the logic of everything happening at all times in the game.
They will be repeated at each frame, so be careful to either condition it to not run everytime, or just not put a thing called once here. 

If you want to read some more indepth code explanation you can read the [system](#systems)

### Archetypes 

Archetypes are optionals but recomended when there's a lot of entity to handle because you can find them directly with the function 
```
pyv.find_by_archetype('yourArchetype')
```
This will allow you to focus directly a certain type of entities, instead of searching them by components.

## Split our code

Usually what we do to have a great ECS implementation is split our game inbetween at least 2 files.

- systems.py
- gamedef.py

Technically, this is the barebone setup for ECS, but we advise adding 2 other files :

- shared.py
- world.py / misc.py

Let's explain them except for gamedef, as this one is really different inbetween games.

If you want to see more indepth code, go in our [Breakout clone tutorial](<../Game Tutorials/Breakout.md>)

## Systems.py

System will host all of your ECS systems.
Let's take our breakout clone as an example of what a system file might look like.

```py
from . import shared
from . import pimodules

pyv = pimodules.pyved_engine
pyv.bootstrap_e()

__all__ = [
    'controls_sys',
    'physics_sys',
    'rendering_sys',
    'gamectrl_sys',
    'endgame_sys'
]

def controls_sys(dt):
    #Empty for now
            
def physics_sys(dt):
    #Empty for now

def rendering_sys(dt):
    #Empty for now
        
def gamectrl_sys(dt):
    pg = pyv.pygame
    for ev in pg.event.get():
        if ev.type == pg.KEYDOWN and ev.key == pg.K_ESCAPE:
            pyv.vars.gameover = True 

def endgame_sys(dt):
    #Empty for now
```

Of course you'd want to fill up the different systems, but here's a small explanation on how to fill it up.

**Controls** would host your player controls, for example what the different keys would do.

**Physics** will have the different interactions with the game and the entities.

**Rendering** will handle displaying your entities.

**Endgame** is used here to handle the conditions of win/lose for the breakout.

## shared.py

This is a file where you specify your constants or global variables, so that they are all in the same place.

It's pretty straightforward, here's the example of our breakout clone.

```py

screen = None
blocks_pop = None
prev_time_info = None
end_game_label = None  # != None means player cannot move bc he/she lost

# (Size of break-out blocks)
BLOCK_W = 54
BLOCK_H = 30
BLOCK_SPACING = 2
SCR_WIDTH = 960
SCR_HEIGHT = 720
LIMIT = SCR_WIDTH / (BLOCK_W + BLOCK_SPACING)
WALL_X, WALL_Y = 4, 80

# physics
PL_WIDTH, PL_HEIGHT = 110, 25
PLAYER_SPEED = 280
MAX_XSPEED_BALL = 225.0
YSPEED_BALL = 288.0

# ball-related
BALL_INIT_POS = 480, 277
BALL_SIZE = 22
```


## world.py/misc.py

This file will keep most of the functions that are only called a few times or once by your game.

```py
def player_create():
    pyv.new_entity(
        archetype='player',
        speed=0.0,
        controls={'left': False, 'right': False},
        body=pygame.rect.Rect(shared.SCR_WIDTH // 2, 635, shared.PL_WIDTH, shared.PL_HEIGHT)
    )
```
This is still from our breakout game, we only want to create our player entity once, so we put it there, and call it inside the initialisation of the game.
