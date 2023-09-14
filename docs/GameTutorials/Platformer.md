# Tutorial platformer

This tutorial is here to help you build above the foundation of the platformer template available in the **Pyved-CLI**.

If you need further help customizing your game, go read the [**pyved-engine full documentation**](https://gaudiatech.github.io/pyved-engine/).

## Entity Component System (ECS) for Game Development

The **Entity Component System (ECS)** is a software architectural pattern commonly used in game development to manage and organize game objects, their behavior, and their data. It is designed to improve code performance, scalability, and flexibility by separating the game's logic into distinct components and entities.

### Key Components of ECS

1. **Entities**: In ECS, an entity represents a game object or an abstract entity in your game world. An entity is essentially a unique identifier, often just an integer or a handle, that is used to group and manage related components. Entities themselves don't contain any behavior or data; they serve as a way to assemble components.

2. **Components**: Components are the building blocks of an ECS system. Each component represents a single, self-contained piece of data and behavior. For example, in a 2D game, you might have components for position, sprite rendering, physics, and more. Components do not have any logic themselves; they are just containers for data.

3. **Systems**: Systems are responsible for defining the behavior and operations performed on entities that have specific combinations of components. Systems process entities based on the components they contain, and they can perform various tasks such as updating the physics simulation, rendering objects, handling input, and more. Systems are typically where the game's logic resides.


## Codebase

Let's go for a quick tour around the code in order for you to understand best how to customize this template to your liking.

The files to customize are located inside of the `cartridge` folder : 

- `shared.py` : This file will store all of your constants.

- `gamedef.py` : This file will store your game loop thanks to 3 declaration available with pyved, declare_begin that will init your game, declare_update that will keep your update loop, and then declare_end to end the game.
You will also keep your entities setup here.

- `systems.py` : This file will keep the logic of your game through the ECS systems, if you want to implement some kind of logic events, you will have them stored here.

- `World.py` : This file will have your entities creation in the game world.

So let's jump right into it, and make our first feature, a **jetpack** for our player !


## First step : Jetpack creation !

Let's make your first feature : 

We will start simple, and define what we will need for a Jetpack to work :

- Add a Jetpack attribute to the player, your character will need a jetpack to use a jetpack 😊

- A jetpack speed ratio, we could technically use the same speed as the player one, but it feels better to have a difference of speed when switching mode 🚀

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

It displays fine, but we still jump, and no jetpack physics in sight...

Let's fix this !

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

Go to the `gamedef.py` and after everyting is initiated add the following code :

```py
    pyv.preload_assets({
        'sounds': [],
        'assets': ['background.png', 'wall_small.png', 'barry.png']
    }, prefix_asset_folder='cartridge/')
    shared.prepare_game_assets()

```

This is a Pyved features that handles the loading of images from your drive to your program, here we added our background, our wall texture and our player image.

You will see 2 ways to add textures, so you can chose which one you prefer for your game, however, one is underoptimized, and can be harmful to your game if implemented in some cases.

### Underoptimized version

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

``` 
        player_image = pyv.vars.images['barry']
        icon = pygame.transform.scale(player_image, (shared.AVATAR_SIZE, shared.AVATAR_SIZE))
```

Here we load our image fropm the pyved image loader, and then resize it.
This is underoptimized because it is resized everytime the player is loaded, in this case, it is not that problematic since the player is only loaded whenever the level is created.
