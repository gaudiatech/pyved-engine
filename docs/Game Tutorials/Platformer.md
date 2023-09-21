
# Tutorial platformer

This tutorial is here to help you create a platformer game,
by building upon an existing foundation.

We use the platformer template available within the `pyved-engine` package.

More precisely we will use the built-in `pyv-cli` command.

If you need further help for using PYV,
you can always refer to the
[**pyved-engine full docs homepage**](https://gaudiatech.github.io/pyved-engine/).



## Step 0. Getting started

#### Download and init. the game template (Platformer)

If you havent done it yet, to install PYV, type:
```shell
pip install pyved-engine
```
Next, you can type (still in the shell):
```shell
pyv-cli init myGame
pyv-cli play myGame
```
When prompted about the game template, select __2__ to follow this tutorial.

#### File structure

Let's go for a quick tour around the code in order for you to best understand
how to customize this template to your liking.

The files to customize are located inside of the `cartridge` folder : 

- `shared.py` : This file will store all of your constants.

- `gamedef.py` : This file will store your game loop thanks to 3 declaration available with pyved, declare_begin that will init your game, declare_update that will keep your update loop, and then declare_end to end the game.
You will also keep your entities setup here.

- `systems.py` : This file will keep the logic of your game through the ECS systems, if you want to implement some kind of logic events, you will have them stored here.

- `World.py` : This file will have your entity creation in the game world.

When testing that demo, at any time you can press ESCAPE to quit the demo.

Enough chit-chat, let's jump right into coding.

It's time to add our first bonus- feature!
What if we give a **jetpack** to our player?!



## Step 1. All I want is a Jetpack!

Let's make your first feature : 

We will start simple, and define what we will need for a Jetpack to work :

- Add a Jetpack attribute to the player, your character will need it to use a jetpack 😊

- A jetpack speed ratio; we could technically use the same speed as the player one, but it feels better to have a difference of speed when switching mode 🚀

- And finally, the logic !

So, let's start by adding the jetpack attributes to our player.

#### Adding a jetpack component

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

#### Tuning the jetpack power!

This step is pretty straightforward, go inside the `shared.py` file

We will simply add the attribute constant here :
```py
JETPACK_RATIO = 0.05
```

#### Jetpack steering?

This is now the hard part, lets add logic to our code in order to be able to interract with the jetpack.

Let's go inside  `systems.py`, now find the block `def steering_sys(...):`

That chunk of code represents the system that handles the player movement. The way
we will handle our jetpack is to check if our player is using it,
in order to disable the jump if the player is using the jetpack since it will
replace it.
What we need to do is: find the following line..
```py
ctrl['down'] = activekeys[pg.K_DOWN]
```
Right beneath that line, we will add this code:
```py
        if not prevdown_key_value and ctrl['down']:
            ent['jetpack'] = not ent['jetpack']
            print('JETPACK:', ('on' if ent['jetpack'] else 'off'))
```
this will act like a switch on the jetpack flag, tied to the Player entity.

Next, we can go inside the game and check if the console we start it from displays
the jetpack on/off message whenever we press the arrow up key.

It displays fine, but we still jump, no jetpack power is available...
Let's fix this !
Still in steering system, you need to find a chunk of code that looks like this:

```py
        if ent['lower_block']:
            if not prevup_key_value and ctrl['up']:
                ent['accel_y'] -= shared.JUMP_POWER
                ent['lower_block'] = None
```

And this is how we handle our jump mechanic,
we will extend this logic (add a condition over it, make it more complex)
in order to create a scenario where:

In one case: player uses the jetpack, and in the other case player simply jumps.

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

As you can see above, we basically use the same formula to calculate our jumping
acceleration, we just multiply it with the `JETPACK_RATIO` we've set earlier.

If you've modified everything as we explained,
you should be able to trigger the
jetpack (using the DOWN ARROW), and now you (using the UP ARROW)
you will have a new exciting way to *move around our little virtual world!*



## Step 2. adding textures to our game

Our game as of now, works well as a technical demo, but it is a bit sad to
play only with blocks, isn't it ?

So let's fix this !

We will add textures to our walls, our player and a background ! 

Let's setup pydev to distribute the images across the code.
You will need three files:
`background.png`, `wall_small.png`, and `barry.png`.
If you don't want to draw your own pixel art,
we provide you with sample files in the:
[following folder](https://github.com/wkta/pyvTutoZero/tree/83ace51b8d0f576972c75d51b6c0e260cd895910/cartridge)
You can download the 3 and put it in the `cartridge/` folder of your game.

Now open the `metadat.json` file to edit it.
We need list new game assets, in the `assets` field:

```json
"assets": [
    "my_map.ncsv", "background.png", "wall_small.png", "barry.png"
],
```
These assets will get loaded automatically (pre-loading assets is a feature our game engine relies on)
PYV handles the loading of images from your drive to your program.
So we have added our background, our wall texture and our player image.

However, since we are unsure whether the size of our assets matches
the needs of our game, it looks safer to **prepare assets** manually,
by rescaling images.

You will see 2 ways for preparing/rescaling your assets:
 you can chose which one you prefer for your game, however,
one is suboptimized, and can be harmful to the game performance in some cases.

#### Prepare assets: method 1

Let's start with modifying the player entity.

Once again,
go to `gamedef.py`, inside the function `troid_init(...)`
add a component named `icon` add the player archetype:

```py
    pyv.define_archetype('player', (
        'speed',
        'accel_y',
        'gravity',
        'lower_block',
        'body',
        'camera',
        'controls',
        'icon'
    ))
```

Next, go to `World.py`, 
search for the `create_avatar` method.
 Here, at the very beginning of the method,
we will create an `icon` variable,
add the following lines above the `pyv.new_from_archetype(...)` call

```py
        player_image = pyv.vars.images['barry']
        icon = pygame.transform.scale(player_image, (shared.AVATAR_SIZE, shared.AVATAR_SIZE))
```

Then, at the player entity initialization, we can set a value for
the component `icon`:

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

Here we load our image from the pyved image loader, and then resize it.
This is suboptimized because it is resized everytime the player is loaded, in this case, it is not that problematic since the player is only loaded whenever the level is created.

#### Prepare assets: method 2 

Let's now add our background and wall texture, to do so,
we will use another approach from the one before
We will create a dictionnary where all of our images will be kept.
So go into `shared.py` and add at the end of the file, the block:

```py
gam_assets = dict()


def prepare_game_assets():
    global gam_assets
    gam_assets['bg'] = pygame.transform.scale(pyv.vars.images['background'], (WIDTH, HEIGHT))
    gam_assets['wall'] = pygame.transform.scale(pyv.vars.images['wall_small'], (BLOCKSIZE, BLOCKSIZE))
```
Here you can see we created new constants for images,
and transformed them to match the size we're using in the project.

This function needs to be called at the beginning of our program,
so add it in the `init_troid(...)` function, in the `gamedef.py` file.

```python
def troid_init(vms=None):
    pyv.init()
    screen = pyv.get_surface()
    shared.screen = screen
    shared.prepare_game_assets()
```

#### Use assets. For real, just do it

Since all assets are now ready (loaded into the memory at runtime),
the rest of the task is to adapt what's rendered by replacing the colored
squares with real images. To do so, navigate to `systems.py`, in the `rendering_sys`.

Let's first add the background, just after the background fill :

```py
    scr.fill((0, 27, 0))
    scr.blit(shared.gam_assets['bg'], [0, 0])
```

And look for thi chunk of code, we will replace it:

```py
    # draw player!
    disp(scr, pl_ent, 'red')
    # draw blocks
    li_blocks = pyv.find_by_archetype('block')
    for b in li_blocks:
        disp(scr, b, 'blue')
```

The new version is:

```py
 # draw player!
    disp(scr, pl_ent, img=pl_ent['icon'])
    # draw blocks
    li_blocks = pyv.find_by_archetype('block')
    for b in li_blocks:
        disp(scr, b, img=shared.gam_assets['wall'])
```

Watch out, do not modify `mob_blocks` (displayed in orange)
We're all done for that step!

One could add more textures for the moving blocks for example,
but we wanted to keep it as surface level as possible.



## Step 3. Adding a new type of Entity

Now, let's get our hands dirty with some hard stuff!

We will create a block that allows us to change levels.
There's many other way to decline the code used, so be creative.

We will first modify our **map data** and add a new block somewhere,
put it wherever you want.
The **map data** is stored in the file: `my_map.ncsv`
You can see the map is encoded as a matrix of numbers:
0, 1, 2 and 3 are used codes.
0 denotes the empty space for example. 1 denotes regular walls etc.

Let's keep going and declare a new type of block by adding a 4 value somewhere.
It's better to replace a 0 value somewhere on the 15th line (it is approximatively
the floor on which the player is walking)
*by the new value 4*.

#### Modding the game

Data has changed, but not the game itself.

Once your `my_map.ncsv` is saved,
go into `gamedef.py`, where we will add a new **archetype**
As defined before, the archetypes allows us to creates new entities
with special rules.

Go after the existing list of archetypes and let's add our new block, the `tp_block`

```py
    pyv.define_archetype('tp_block', ['body', ])
```

Here we just added the property `body` to our block,
because we just need it to have an actual hitbox, the logic of what happens whenever we reach the blocks is elsewhere.

Now that our archetype exists, we need our world to know who's this new kid in the block.

Go inside the `World.py` file and under the `add_terrain_blocks` function.

Since this function handles the initialisation and properties of blocks,
let's add the logic:
how to process our value "4", link it to a `tp_block` entity:
Be careful, this needs to be added **inside the for loop**, not outside.

```py
            elif btype == 4:
                pyv.init_entity(
                    pyv.new_from_archetype('tp_block'), {
                        'body': rrect
                    }
                )
                self._platforms.append(rrect)
```

We give the property ``rect`` to the `body`, 
this will allow us to give the block a proper hitbox.

Now we will take a small break from all of this hard stuff,
and create our new map, we will need it to load somewhere.
Just create a `map2.ncsv` file by copying the first one and change
a few blocks here and there!

Also make sure that you list the: `map2.ncsv` file in your
list of assets to load, as specified in your `metadat.json` file
(just append the name `map2.ncsv` at the end af the existing asset list)


#### Loading another world

*We're almost done!*

*Hang in there! You're doing great.*

Go to `systems.py` and draw our new block on the map,
go back to the same place where we previously (Step 2. of the tutorial)
changed how way blocks are displayed. It's around line 200 of that file.
Add the following line after the display of orange blocks:

```py
    temp = pyv.find_by_archetype('tp_block')
    if len(temp):
        tp_block = temp[0]
        disp(scr, tp_block, 'purple', 3)
```

Now that the block is present on the map,
let's add some logic for it,
in order to make it truly a new feature.

We will
call a function named `_proc_unload_load`, that is already defined.
You don't need to worry about writing that part, but it can
be useful for you to understand how we proceed.

In that pre-defined function, all we do is using the
component `next_map` to tell
the game where the player should be teleported to,
and we re-create the avatar entity. Here's the code we refer to:
```py
def _proc_unload_load():
    player = pyv.find_by_archetype('player')[0]
    camref = player['camera']
    pyv.wipe_entities()
    shared.world.load_map(player['next_map'])
    shared.world.create_avatar(camref)
```

Now, go inside the `teleport_sys` (a system that handles player teleportation),
at the end of that function please add:

```py
    temp = pyv.find_by_archetype('tp_block')
    if len(temp):
        tp_block = temp[0]
        if player['body'].colliderect(tp_block['body']):
            player['next_map'] = 'map2'
            _proc_unload_load()
```

Here what we're doing is creating a var `temp` that will reference
our `tp_block`, and thanks to `colliderect` we will detect if the 2 blocks
are colliding.
Once they collide, we just move our player to the next map, by unloading
the current map and loading the next one.

Hopefully, your game now looks like this!
You are now able to travel between two different worlds...
Two independant maps!

![The patformer end result](./img/screenshot.png "Our game")

Et voila... You're done!
Amazing isn't it?
**Congrats for completing this tutorial.**

If something is wrong/ if the program crashes, make sure to read again all
previous steps, one by one and check if you haven't forgot anything.
In case this is not enough to find the solution, you can always join our
[Discord community](https://discord.gg/SHdJhcWvQD) and ask for help. *More advanced PYV users will be glad to help you!*

Now go ahead, imagine a fourth or even a fifth feature to add by yourself!
One interesting feature for example could be: a special code in the map model,
to specify where the player should respawn...

But hey, it's your role to be creative! You are a game dev now.
Have fun, coding with PYV.
