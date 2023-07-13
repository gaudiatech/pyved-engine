
<p align="center">
  <img src="https://gaudia-tech.com/shared/pyv-logo.jpg" alt="pyv logo" />
</p>

Introducing `pyved-engine`, a Python package that provides
a powerful and efficient 2D game engine named **Pyv**.

Designed to streamline game development **Pyv** offers a comprehensive set of
tools for rapid prototyping and game production.

Create captivating and bug-free applications effortlessly. **Pyv** offers an
array of built-in modules for seamless management of game assets, AI integration,
procedural generation, and other advanced features. Join our vibrant community
today and unlock the full potential of your game development with **Pyv**!

<p align="center">
  <a href="https://discord.gg/SHdJhcWvQD">
  <img alt="join us on Discord" src="https://img.shields.io/discord/876813074894561300.svg?label=&logo=discord&logoColor=ffffff&color=7389D8&labelColor=6A7EC2">
  <br>Join our Discord
  </a>
</p>

### Why not simply use Pygame?

There seems to be some confusion within the community regarding the
distinction between a Python package and a game engine. It's important to
note that Pygame, while being a Python package, does not offer the comprehensive
set of features found in a dedicated 2D game engine. As a result, it may not
fulfill all the requirements necessary for developing a fully-fledged game.

### How can a game engine help me?

A game engine provides invaluable time-saving benefits by storing a collection
of useful and reusable code snippets within its framework.
Instead of reinventing the wheel and wasting your precious time by re-writing
generic code for video games, you can leverage the power of the engine.

By referring to the comprehensive documentation, you can quickly learn how to
implement various functionalities such as pathfinding or loading spritesheets.
With simple function or method calls, you can seamlessly integrate these
features into your game, saving precious development time and effort!

### Getting started

To install our Python package, simply type:
```shell
pip install pyved-engine
```
Once **Pyv** is available on your system, to begin,
open a command line and create a new game by typing the following command:
```shell
pyv-cli create [MyGame]
```
Replace [MyGame] with any fancy name you prefer for your game. This command
will initialize your project and generate a boilerplate source code. For the
sake of clarity, we have copied the boilerplate code below:

```python
import pyved_engine as pyv

pyv.init(pyv.HD_MODE)
```

### Read/improve the technical documentation

The documentation isn't finished. Your help would be very appreciated to improve
that part. Files used to build the documentation can be found within the `docs\`
folder, there is also the `mkdocs.yml` file that is located at the root folder of
the project.

To preview the bleeding edge version of docs, you can type:
```shell
mkdocs build
mkdocs serve
```
If it doesn't work, remember that you needed the `mkdocs` python lib first.
To fix this rapidly you can type: `pip install -r requirements.txt`

For now, the documentation is available in only two languages: English and French.

of video games)
* a wrapper around the popular [pygame lib](https://github.com/pygame/pygame)
* the abbreviation for [__k__]ata [__engi__]ne

Why "kata"?
[Kata.Games](https://kata.games) denotes a new gaming platform that helps indie game developers to create and share
digital experiences easily, all around the globe!
Via this innovative platform, we're proud to publish all kinds of games powered by `pyved-engine`.


# For advanced user

## Design principles

1. Code readability matters. Clean, expressive code is not a luxury!

2. `pyved-engine` encourages the use of patterns such as the Mediator or MVC,
but people should remain free to use their favorite coding style.

3. `pyved-engine` will be embedded in a versatile toolbox simply named `pyved`

## Feature Overview
The game engine comes packed with useful features:
1. global event queue (simplifies the use of both the Mediator and the MVC design patterns)
2. gamestate stack, state management via events 
3. simple GUI creation: buttons, checkboxes, *etc.* 
4. tileset loading, sprite animation
5. tilemap parser (based on `.tmx` or `.tsj` file formats)
6. mathematical tools: matrices ; vectors ; gradient noise functions (->procedural generation)
7. helper classes for coding roguelike or RPG games
8. helper classes for coding card games (Poker, Blackjack, *etc.*)
9. helper classes for adding artificial opponents/intelligent entities (NPCs) to your game
10. ...


## Installation
To get started, first, copy the source-code (as a .zip file) from Github. It is recommended to download the last tagged version,
(not the most recent commit) because most recent dev versions might be unstable.

Once you have the files on your computer, use the command line to navigate to the root folder of the project (one level below `src\`).

Because `pyved-engine` is still in an *alpha* phase,
it is recommended to clone the repository by yourself and
then use the command line to install `pyved-engine` in an editable
mode.
```shell
> git clone https://github.com/gaudiatech/pyved-engine.git .
> cd pyved-engine
> pip install -e .
```
These 3 lines install `pyved-engine` on your system, but also
allow you to modify the source-code of the engine.

## Getting started

To test `pyved-engine` right away, you could
create an empty file named `test_engine.py`.
Then copy-paste the basic code snippet below, it shows you how
a game can be built.
```python
import pyved_engine as pve

HELP_MSG = 'press ESC to exit, any key to change bg_color...'
CAPTION = 'my first video game, hi mom!'

pve.init(1, caption=CAPTION)
pygame = pve.pygame
screen = pve.get_surface()
color_idx = 0
allcolors = ('pink', 'yellow', 'purple')
bg_color = allcolors[0]
print(HELP_MSG)
gameover = False

while not gameover:  # game loop
    for ev in pygame.event.get():
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                gameover = True
            else:
                color_idx = (color_idx + 1) % len(allcolors)
    # update "game logic"
    bg_color = allcolors[color_idx]
    # update the display
    screen.fill(bg_color)
    pve.flip()

print('done!')
```
This is only one possibilty, very similar to how you 
define games using `pygame-ce`. In *the docs* you will see better,
more efficient ways to define your games.


## Mini tutorial
If you're familiar with `pygame`, getting used to `pyved-engine` is really easy.
Navigate to the `src/` folder. There, you see a very basic example that uses only pygame:
* [demo-a-pygame.py](https://github.com/gaudiatech/pyved-engine/blob/master/src/demo-a-pygame.py)

Now try to notice what is different when one uses `pyved-engine` (only minor details change):
* [demo-a-kengi-straightf.py](https://github.com/gaudiatech/pyved-engine/blob/master/src/demo-a-kengi-straightf.py)

This is only one way to use `pyved-engine` but it's most likely that you will start with this one,
if you already have some background in creating games using `pygame`.
Actually, one can see `pyved-engine` as a mere wrapper around pygame. Everything that you can do
with `pygame` can be done the same way when using `pyved-engine`, but `pyved-engine` also unlocks
many new features that are very worthy of interest!

To explore more possibilities you can take a glimpse of the next demo
that implements the same thing but using the M-V-C pattern:
* [demo-a-kengi-mvc.py](https://github.com/gaudiatech/pyved-engine/blob/master/src/demo-a-kengi-mvc.py)

Note that this program starts with the declaration
of a list of user-defined events. User-defined events can have attributes.
These events, just like regular pygame events, are processed via a standard method
`proc_event` that you need to re-define when you sub-class
`pyved-engine.event.EventReceiver`...

## General goal
As a wise man (Joel Spolsky) once said:
> "It’s Harder to Read Code than to Write it"

Our general goal is to empower you to:

1. **write standardized therefore very easy-to-read code**

Readability is not to overlook! If you take care of your code readability you'll encounter
30% fewer bugs, you will fix any bug faster, etc. It works like magic!

2. **write a type of code that can evolve easily**

By using our *built-in event system* along with the *M-V-C pattern*, you can reach
an amazing level of code flexibility.

3. **be more productive**

And, interestingly enough:

5. **distribute your newly created games via our awesome
[Kata.Games](https://kata.games) platform!**

In this way, your whole game and the python source-code that it's made of, can be
played directly by modern browser (Chrome, Brave, etc.). *A world premiere!*


## License
Currently, materials in this repo are all licensed under the LGPL3 license.
See the `LICENSE` file for more info.


## Contribute
Feel free to join the developer team. It's a super easy two-step process:
(a) start by forking `pyved-engine`,
 (b) join our Discord to discuss, or create a Pull Request directly!

If you spot a bug, create an issue and tell us how to reproduce the bug.
The documentation is built via the `mkdocs` tool. Feel free to make it more user-friendly! It's as simple as modifying a few text files in the `docs/` folder.
Pull Requests are much appreciated!

Newcomers are always welcome,
below are listed the 10 first contributors –our Hall of fame– ;-)
* [wkta-tom](https://github.com/wkta) architecture, event system, design patterns
* [tank-king](https://github.com/tank-king) fancy game templates (flappy bird, match3)
* [jwvhewitt](https://github.com/jwvhewitt) isometric engine
* ...
