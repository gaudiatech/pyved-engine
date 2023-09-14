# Tutorial platformer

This tutorial is here to help you build upon the foundation of the platformer template available in the **Pyved-CLI**.

If you need further help customizing your game, go read the [**pyved-engine full documentation**](https://gaudiatech.github.io/pyved-engine/).

## Entity Component System (ECS) for Game Development

The **Entity Component System (ECS)** is a software architectural pattern commonly used in game development to manage and organize game objects, their behavior, and their data. It is designed to improve code performance, scalability, and flexibility by separating the game's logic into distinct components and entities.

### Key Components of ECS

1. **Entities**: In ECS, an entity represents a game object or an abstract entity in your game world. An entity is essentially a unique identifier, often just an integer or a handle, that is used to group and manage related components. Entities themselves don't contain any behavior or data; they serve as a way to assemble components.

2. **Components**: Components are the building blocks of an ECS system. Each component represents a single, self-contained piece of data and behavior. For example, in a 2D game, you might have components for position, sprite rendering, physics, and more. Components do not have any logic themselves; they are just containers for data.

3. **Systems**: Systems are responsible for defining the behavior and operations performed on entities that have specific combinations of components. Systems process entities based on the components they contain, and they can perform various tasks such as updating the physics simulation, rendering objects, handling input, and more. Systems are typically where the game's logic resides.


## Codebase

Let's go for a quick tour around the code in order for you to best understand how to customize this template to your liking.

The files to customize are located inside of the `cartridge` folder : 

- `shared.py` : This file will store all of your constants.

- `gamedef.py` : This file will store your game loop thanks to 3 declaration available with pyved, declare_begin that will init your game, declare_update that will keep your update loop, and then declare_end to end the game.
You will also keep your entities setup here.

- `systems.py` : This file will keep the logic of your game through the ECS systems, if you want to implement some kind of logic events, you will have them stored here.

- `World.py` : This file will have your entity creation in the game world.

So let's jump right into it, and make our first feature, a **jetpack** for our player !


## First step : Jetpack creation !

Let's make your first feature : 

We will start simple, and define what we will need for a Jetpack to work :

- Add a Jetpack attribute to the player, your character will need it to use a jetpack 😊

- A jetpack speed ratio; we could technically use the same speed as the player one, but it feels better to have a difference of speed when switching mode 🚀

- And finally, the logic !

So, let's start by adding the jetpack attributes to our player.

### Giving our character a jetpack attribute

Go into `World.py` and `gamedef.py` 

`World.py`  We first have this code : 
```py
        pyv.init_entity(player, {
            'speed': [0.0, 0.0],
            'accel_y': 0.0,
            'gravity': 14.5,
            'lower_block': None,
            'body': pygame.rect.Rect(shared.SPAWN[0], shared.SPAWN[1], shared.AVATAR_SIZE, shared.AVATAR_SIZE),
            'camera': cam_ref,
            'controls': {'up': False, 'down': False, 'left': False, 'right': False}
            })
```

We will add a jetpack attribute inside of the player entity 

```py 
        pyv.init_entity(player, {
            'speed': [0.0, 0.0],
            'accel_y': 0.0,
            'gravity': 14.5,
            'lower_block': None,
            'jetpack': False,
            'body': pygame.rect.Rect(shared.SPAWN[0], shared.SPAWN[1], shared.AVATAR_SIZE, shared.AVATAR_SIZE),
            'camera': cam_ref,
            'controls': {'up': False, 'down': False, 'left': False, 'right': False}
            })
```

Now, let's dive into the `gamedef.py` file : 

```py
    pyv.define_archetype('player', (
        'speed', 'accel_y', 'gravity', 'lower_block', 'body', 'camera', 'controls'
    ))
```

And we also add the jetpack here :

```py
    pyv.define_archetype('player', (
        'speed', 'accel_y', 'gravity', 'lower_block', 'jetpack', 'body', 'camera', 'controls'
    ))
```

### Jetpack speed !


This step is pretty straightforward, go inside the `shared.py` file

We will simply add the attribute constant here :
```py
JETPACK_RATIO = 0.05
```

### The jetpack logic

This is now the hard part, lets add logic to our code in order to be able to interract with the jetpack.

Let's go inside  `systems.py`, now go inside the steering system, this is the system that handles the player movement.

The way we will handle our jetpack is to check if our player is using it, in order to disable the jump if the player is using the jetpack since it will replace it.

Let's first add this code just after the control definition
```py
        if not prevdown_key_value and ctrl['down']:
            ent['jetpack'] = not ent['jetpack']
            print('JETPACK:', ('on' if ent['jetpack'] else 'off'))
```

Now, we can go inside the game and check if the console we start it from displays the jetpack on/off message whenever we press the arrow up key.

It displays fine, but we still jump, and no jetpack physics in sight...Let's fix this !

```py
        if ent['lower_block']:
            if not prevup_key_value and ctrl['up']:
                ent['accel_y'] -= shared.JUMP_POWER
                ent['lower_block'] = None
```

This is how we handle our jump mechanic, let's add a condition over it, in order to create a case where we will use the jetpack, and in the other the jump.

```py
        if not ent['jetpack']:
            if ent['lower_block']:
                if not prevup_key_value and ctrl['up']:
                    ent['accel_y'] -= shared.JUMP_POWER
                    ent['lower_block'] = None
        else:  # other rules apply!
            if ctrl['up']:
                ent['accel_y'] = -shared.JUMP_POWER * shared.JETPACK_RATIO
```

As you can see above, we basically use the same formula to calculate our jumping acceleration, we just multiply it with the `JETPACK_RATIO` we've set earlier.

And now, if you did everything correctly, you should be able to trigger the jetpack, and you will have a new exciting way to move around the gameworld !


## Second step : Adding textures to our game

Our game as of now, works well as a technical demo, but it is a bit sad to play only with blocks, isn't it ?

So let's fix this !

We will add textures to our walls, our player and a background ! 

Let's setup pydev to distribute the images across the code.

Go to the `gamedef.py` and after everything is initiated add the following code :

```py
    pyv.preload_assets({
        'sounds': [],
        'assets': ['background.png', 'wall_small.png', 'barry.png']
    }, prefix_asset_folder='cartridge/')
    shared.prepare_game_assets()

```

This is a Pyved features that handles the loading of images from your drive to your program, here we added our background, our wall texture and our player image.

You will see 2 ways to add textures, so you can chose which one you prefer for your game, however, one is suboptimized, and can be harmful to your game if implemented in some cases.

### Suboptimized version

Let's start with our player

Go to `World.py`, and search for our player entity again, we will add a new property, named `icon`

```py
        pyv.init_entity(player, {
            'speed': [0.0, 0.0],
            'accel_y': 0.0,
            'gravity': 14.5,
            'lower_block': None,
            'jetpack': False,
            'body': pygame.rect.Rect(shared.SPAWN[0], shared.SPAWN[1], shared.AVATAR_SIZE, shared.AVATAR_SIZE),
            'camera': cam_ref,
            'controls': {'up': False, 'down': False, 'left': False, 'right': False},
            'icon': icon
        })
```

Now the player can have an image, but let's create this icon variable.
Add the following lines just above your player entity.

```py
        player_image = pyv.vars.images['barry']
        icon = pygame.transform.scale(player_image, (shared.AVATAR_SIZE, shared.AVATAR_SIZE))
```

Here we load our image from the pyved image loader, and then resize it.
This is suboptimized because it is resized everytime the player is loaded, in this case, it is not that problematic since the player is only loaded whenever the level is created.

### Optimized version 

Let's now add our background and wall texture, to do so, we will use another approach from the one before

We will create a dictionnary where all of our images will be kept.

So go into `shared.py`

```py
gam_assets = dict()


def prepare_game_assets():
    global gam_assets
    gam_assets['bg'] = pygame.transform.scale(pyv.vars.images['background'], (WIDTH, HEIGHT))
    gam_assets['wall'] = pygame.transform.scale(pyv.vars.images['wall_small'], (BLOCKSIZE, BLOCKSIZE))
```
Here you can see we created new constants for images, and transformed them to match the size we're using in the project.

We will now just need to adapt what's rendered by replacing the colored squares with our images.

To do so, go into `systems.py` into the `rendering_sys`.

Let's first add the background, just after the background fill :

```py
    scr.fill((0, 27, 0))
    scr.blit(shared.gam_assets['bg'], [0, 0])
```

And now replace the colors with our images :

```py
    # draw player!
    disp(scr, pl_ent, 'red')
    # draw blocks
    li_blocks = pyv.find_by_archetype('block')
    for b in li_blocks:
        disp(scr, b, 'blue')
```

```py
 # draw player!
    disp(scr, pl_ent, img=pl_ent['icon'])
    # draw blocks
    li_blocks = pyv.find_by_archetype('block')
    for b in li_blocks:
        disp(scr, b, img=shared.gam_assets['wall'])
```

And now we're all done here ! 

You can still add more texture for the moving blocks for example, but we wanted to keep it as surface level as possible.


## Step 3 : Add a new type of Entity

Now, let's get our hands dirty with the hard stuff !

We will create a block that allows us to change levels.
There's many other way to decline the code used, so be creative.

We will first modify our map and add a new block somewhere, put it wherever you want.

You can see the map uses 0, 1, 2 and 3 as blocks, so let's keep going and create our new block by adding a 4 in the map.

Let's now go into `gamedef.py` and we will add a new **archetype**

As defined before, the archetypes allows us to creates new entities with special rules.

Go after the other archetypes and let's add our new block, the `tp_block`

```py
    pyv.define_archetype('tp_block', ['body', ])
```

Here we just added the property `body` to our block, because we just need it to have an actual hitbox, the logic of what happens whenever we reach the blocks is elsewhere.

Now that our archetype exists, we need our world to know who's this new kid in the block.

Go inside the `World.py` file and under the `add_terrain_blocks` function.

Since this function handles the initialisation and properties of blocks, let's add our `tp_block`

```py
            elif btype == 4:
                pyv.init_entity(
                    pyv.new_from_archetype('tp_block'), {
                        'body': rrect
                    }
                )
                self._platforms.append(rrect)
```

We give the property ``rect`` to the `body`, this will allow us to give the block a proper hitbox.

Now we will take a small break from all of this hard stuff, and create our new map, we will need it to load somewhere.

Just create a `map2.csv` file, or copy the first one and change a few things here and there.

And let's finish this !

Go to `systems.py` and draw our new block on the map, go back to the same place where we changed the colors into images and add the following line :

```py
    temp = pyv.find_by_archetype('tp_block')
    if len(temp):
        tp_block = temp[0]
        disp(scr, tp_block, 'purple', 3)
```
