# ECS in code

Here we'll explain to you in further detail how we implement ECS with PYV.


## Syntax

Let's explain the syntax to code some of the basic code needed for ECS implementation.


### Entities

To create an entity one can use the following syntax:
```python
    pyv.new_entity(component1=value_x, component2=value_y)
```
Where `value_x` and `value_y` can contain any type of Pyhon vue or expression.
That is the syntax of creating a new entity using PYV.

Now let's see a more precise implementation examples in order to show some more possibilities.
Here for example we wish to build an entity to model the player...
```py
    player = pyv.new_entity(
        speed=0.0,
        controls={'left': False, 'right': False},
        body=pygame.rect.Rect(
            shared.SCR_WIDTH // 2, 635, shared.PL_WIDTH, shared.PL_HEIGHT
        )
    )
```

To do so we specify all useful components, such as the player speed,
the controls, and the hitbox. (We could use an archetype for more clarity, but this
will explained a bit further. Also, using archetypes is not mandatory).
In practice, you'd create most entities of your game and call these functions
at the initialization of the game.


### Components

As shown before, the components are part of an entity, the components can be pretty much everything.
It's a characteristic of an entity, could be speed, hit points, position and so much more...

You can call your entities by their components with 
```
pyv.find_by_components('yourComponent')
```

### Systems

The purpose of systems is to describe the logic of everything that happens
between two frames of the game.
Systems are active (repeated) before each frame display. Be careful to add
conditions to your computations (when appropriate) so you don't run heavy computations
everytime. You can use boolean flags or various tests to know wether a system really needs
to update entities in your games, or not!

If you want to learn more about this topic, you could check out the example
that is given in the [Systems.py example](#ConcreteSystemsPy) showed below.

### Archetypes 

Archetypes are optionals but recomended when there's a lot of entity to handle because
you can find them directly with the function
```
pyv.find_by_archetype('yourArcheName')
```
This will allow you to focus directly a certain type of entities, instead of searching
them by components.


## Structure of a game

When using ECS to its full potential, what we do is typically splitting our game
inbetween three files:

- `systems.py`
- `shared.py`
- `gamedef.py`

This is the barebone setup for ECS, but we also advise game devs to add one or two
more files:

- `world.py` and maybe `misc.py`

Let's explain them except for gamedef, as this one is really different inbetween games.

If you want to see more indepth code,
go check our [breakout clone tutorial](<../GameTutorials/Breakout.md>)

### <a name="ConcreteSystemsPy"></a> File: systems.py

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

### File: shared.py

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


### Files: world.py and misc.py

The role of the last two files you can use in your project,
is to keep the bulk of complex functions, or functions that are only called a few times
by your game in a different place...

As we don't want `systems.py` to become too messy/difficult to read.
For example:

```py
def player_create():
    pyv.new_entity(
        archetype='player',
        speed=0.0,
        controls={'left': False, 'right': False},
        body=pygame.rect.Rect(shared.SCR_WIDTH // 2, 635, shared.PL_WIDTH, shared.PL_HEIGHT)
    )
```

This would be useful in a `world.py` file, for a breakout clone.
We only wish to create our player entity once,
so we put it there, and call it inside the init function of the game.
