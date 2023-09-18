# Tutorial Breaker

This tutorial is here to help you create a block breaker type game from scratch.

This tutorial can also be used as a nice base to understand and experiment with the ECS pattern.

Note that the game in it's final state is already available in the `pyved-engine` in the `pyv-cli`.


If you need further help for using PYV,
you can always refer to the
[**pyved-engine full docs homepage**](https://gaudiatech.github.io/pyved-engine/).


## Step 0. Getting Started

### Either Download the init, or just the template

If you want to build upon the foundation of the breaker template, you can download it by doing the following

```shell
pyv-cli init myGame
pyv-cli play myGame
```
And choose the Breakout template.

Note that this tutorial won't focus on building upon the foundation, instead the focus is on how to build on nothing and manage to create such a game.

So for this, we will choose the empty template instead.

Your folder should look something like this.

    .
    └── YourBundleName/
        ├── cartridge/
        │   ├── __pycache__/
        │   ├── gamedef.py
        │   ├── __init__.py
        │   ├── metadat.json
        │   └── pimodules.py
        ├── __pycache__/
        ├── __init__.py
        ├── vm.py
        └── vmslateL.py


## Step 1 : Create the necessary files for the ECS 

As of now, all of the files used in an ECS configuration aren't auto generated, this might change in the future, but since you're here to learn everything on how to create a game using Pyved and ECS, let's get into it.

Go inside `cartridge` and create the following file, they'll be useful later :

- shared.py
- systems.py
- world.py

These files will store nearly all of your ECS code.

## Step 2 : Creating the foundations

In this part, you will learn how to create your first entities and draw them on your screen.

### Creation of Archetypes and Entities

First, let's create all of our constants in our `shared.py` :

```py
import random


screen = None
blocks_pop = None

# (Size of break-out blocks)
BLOCK_W = 54
BLOCK_H = 30
BLOCK_SPACING = 2
WALL_X, WALL_Y = 4, 80
PLAYER_SPEED = 10

# ball-related
BALL_INIT_POS = 480, 277
BALL_SIZE = 22
RANDOM_DIR = random.uniform(-5.0, 5.0)
```
We will use all of those constants laters, but they are important.


Secondly we will create all of our entities, let's head inside `gamedef.py`

``` py
from . import pimodules
from . import shared
from . import systems
from .world import world

pyv = pimodules.pyved_engine
@pyv.declare_begin
def init_game(vmst=None):
    pyv.init(wcaption='Néant')
```

Let's create our archetypes, this is how we will create the different entities : 

```py
    pyv.define_archetype('player', (
        'speed', 'controls', 'body'
    ))
    pyv.define_archetype('block', ('body', ))
    pyv.define_archetype('ball', ('body', 'speed'))
```

We can now go into `world.py`, to create our entities :

```py
from . import shared
from . import pimodules
pyv = pimodules.pyved_engine

pygame = pyv.pygame


class world:

    def create_player():
        player = pyv.new_from_archetype('player')
        pyv.init_entity(player, {
            'speed': 0.0, 
            'controls':{'left': False, 'right': False},
            'body': pygame.rect.Rect(900,600, shared.BLOCK_W, shared.BLOCK_H)
        })

```

We are creating a create_player function, this will create the entities with our default settings, we will do the same for every entity present in our game.

We give it, a speed, some controls, here we only give it left and right, as we don't need other directions.

And finally a body, so that our player have a hitbox.

```py
    def create_ball():
        ball = pyv.new_from_archetype('ball')
        pyv.init_entity(ball, {
            'speed': 0.0, 
            'body': pygame.rect.Rect(shared.BALL_INIT_POS[0],shared.BALL_INIT_POS[1], shared.BALL_SIZE, shared.BALL_SIZE)
        })
```

We will create our ball too, we will keep the same logic, and create, it needs a speed to move, and a hitbox to detect collisions.


```py
def create_blocks():
        bcy = 0 
        LIMIT = 960/(shared.BLOCK_W + shared.BLOCK_SPACING)
        for column in range(5):
            bcy = bcy+shared.BLOCK_H + shared.BLOCK_SPACING
            bcx = -shared.BLOCK_W
            for row in range(round(LIMIT)):
                bcx = bcx +shared.BLOCK_W + shared.BLOCK_SPACING
                rrect = pygame.rect.Rect(0 + bcx, 0 + bcy, shared.BLOCK_W, shared.BLOCK_H)

                pyv.init_entity(pyv.new_from_archetype('block'),{
                    'body': rrect
                })
```

Here the code is a bit different, since there's more than one block, we will loop over it to generate as many entity as needed.

Here we fill the screen from left to right, and on 5 row with blocks.

We can now head back into `gamedef.py` and finalise the creation of our entities.


```py
@pyv.declare_begin
def init_game(vmst=None):
    pyv.init()
    pyv.define_archetype('player', (
        'speed', 'controls', 'body'
    ))
    pyv.define_archetype('block', ('body', ))
    pyv.define_archetype('ball', ('body', 'speed'))
    world.create_player()
    world.create_ball()
    world.create_blocks()
    pyv.bulk_add_systems(systems)
```
Here we added the call to the different functions we made in the `world.py`, so that now, when we launch our game, we create actual entities instead of just their archetypes.

As for the line `pyv.bulk_add_systems(systems)` we will get back to it soon.

### Creating systems

The systems are an essentiel part of the ECS, it's basically all of the logic happening in the game.


Let's head inside `systems.py` :

```py
from . import shared
from . import pimodules
pyv = pimodules.pyved_engine
pyv.bootstrap_e()

__all__ = [

    'gamectrl_sys'
]

def gamectrl_sys(entities, components):
    pg = pyv.pygame
    for ev in pg.event.get():
        if ev.type == pg.KEYDOWN and ev.key == pg.K_ESCAPE:
            pyv.vars.gameover = True 

```

This is a base setup for a `systems.py` file, let's make it a bit more full with all of our base systems.

```py
from . import shared
from . import pimodules

pyv = pimodules.pyved_engine
pyv.bootstrap_e()

__all__ = [
    'controls_sys',
    'physics_sys',
    'rendering_sys',
    'gamectrl_sys'
]

def controls_sys(entities, components):
    #Empty for now
            
def physics_sys(entities, components):
    #Empty for now

def rendering_sys(entities, components):
    #Empty for now
        
def gamectrl_sys(entities, components):
    pg = pyv.pygame
    for ev in pg.event.get():
        if ev.type == pg.KEYDOWN and ev.key == pg.K_ESCAPE:
            pyv.vars.gameover = True 

```

Now, we will create our rendering system, to at least have some graphics and wrap this step up.

```py
def rendering_sys(entities, components):
    """
    displays everything that can be rendered
    """
    scr = shared.screen

    scr.fill((0, 0, 0))
    pl_ent = pyv.find_by_archetype('player')[0]
    li_blocks = pyv.find_by_archetype('block')
    ball = pyv.find_by_archetype('ball')[0]

    pyv.draw_rect(scr, 'white', pl_ent['body'])
    pyv.draw_rect(scr, 'blue', ball['body'])
    for b in li_blocks:
        pyv.draw_rect(scr, 'purple', b['body'])
```

What we do here, is first fill the screen in black, then find the different lists of entities for each archetypes.

We then simply give their hitbox a graphical representation with different colors.

Since the player and ball are alone, we just go for the first one of the list, and we iterate over the different blocks we created before.

Let's head one last time into `gamedef.py`, and add the few details missing in order to display everything fine.

```py

@pyv.declare_begin
def init_game(vmst=None):
    pyv.init()
    screen = pyv.get_surface() 
    shared.screen = screen
    pyv.define_archetype('player', (
        'speed', 'controls', 'body'
    ))
    pyv.define_archetype('block', ('body', ))
    pyv.define_archetype('ball', ('body', 'speed'))
    world.create_player()
    world.create_ball()
    world.create_blocks()
    pyv.bulk_add_systems(systems)
```
Here we added the screen creation to our initialisation sequence, this is also where the bulk system is used, since we created a rendering system, we need to load it in our game.

Now, in order to have something displays and refresh, we will also modify our update like so:

```py
@pyv.declare_update
def upd(time_info=None):
    pyv.systems_proc()
    pyv.flip()
```
Here we use our systems, then use flip in order to display everything.

And now, your game should look something like this 

![Breakout mid](./img/breakoutmid.png "Our breakout base")

So, as of now, we can display things on our screen, but nothing more happens.

We will change this in the 3rd step, we will start adding movement and interactions for everything.

## Step 3 : Making our game

