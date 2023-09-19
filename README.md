<p align="center">
  <img src="https://gaudia-tech.com/shared/pyv-logo.jpg" alt="pyv logo" />
</p>

Introducing `pyved-engine`, a Python package that provides you with
the versatile, efficient 2D game engine named PYV!
Designed to streamline game development, PYV offers a set of
tools for smooth and rapid game prototyping.

Unlock the full potential of your game development thanks to __pyv__!

<p align="center">
<a href="https://discord.gg/SHdJhcWvQD">
To join our Discord community:<br>
<img alt="join us on Discord" src="https://img.shields.io/discord/876813074894561300.svg?label=&logo=discord&logoColor=ffffff&color=7389D8&labelColor=6A7EC2">
</a>
</p>



## 1. Introduction

### Cpabilities of a game engine

A game engine provides invaluable time-saving benefits by storing a collection
of useful and reusable code snippets within its framework.
Instead of reinventing the wheel and wasting your precious time by re-writing
generic code for video games, you can leverage the power of the engine.

By referring to the
[work-in-progress documentation](https://gaudiatech.github.io/pyved-engine/), you
could quickly learn how to implement various functionalities such as pathfinding
or loading spritesheets. With simple function or method calls, you can seamlessly
integrate these features into your game, saving precious development time
and effort!

Create captivating and bug-free applications effortlessly. __pyv__ offers an
array of built-in modules for seamless management of game assets, AI integration,
procedural generation, and other advanced features.


### Vision and goals

The vision behind the work done on PYV is as follows:


* __Write standardized therefore very easy-to-read code__:
readability is not to overlook! If you take care of your code readability you'll
encounter 30% fewer bugs, you will fix any bug faster, etc. It works like magic!
 
As a wise man said:
> "It’s Harder to Read Code than to Write it"\
> — Joel Spolsky

* __Write a type of code that can evolve easily__: by using the *built-in event
system* along with one pattern amongst: Mediator, MVC, ECS you should reach
a high level of code flexibility
* __Be more productive__
* __One new optionnal feature brought by PYV: to allow one (if one wishes)
to distribute one's games__ via a new gaming platform named
[https://kata.games](https://Kata.Games) |
In that way, your Python game can be played directly 
in any modern browser (Chrome, Brave, *etc*).

### How do Pyv and Pygame differ?

Confusion appears to exist within the community regarding the differentiation
between a Python package, and a game engine.

It's crucial to understand that *although Pygame functions as a regular
Python package/library*.
It doesn't provide the extensive array of features present
in a specialized 2D game engine! Consequently, it might not satisfy all the
prerequisites essential for the development of a fully-realized game.

Furthermore, it's worth noting that distributing games created using Pygame
can present challenges. For instance, generating an executable from a Pygame
project often requires reliance on third-party tools, adding an extra layer
of complexity to the process. Sharing such an executable via platforms like
Steam can also prove to be remarkably time-consuming, involving various steps
that can be quite daunting, especially for newcomers.

This underscores the importance of considering not just the development
capabilities, but also the subsequent distribution and accessibility of the
final product. While Pygame has its merits, these distribution-related hurdles
can significantly impact the overall experience of bringing your game to 
the world.

### Details about game engine features

The game engine comes packed with a ton of features:

1. event queue (simplifies the use of patterns such as: Mediator, the MVC pattern)
2. gamestate stack, state management via events 
3. simple GUI creation: buttons, checkboxes, *etc.* 
4. tileset loading, sprite animation
5. tilemap parser (based on `.tmx` or `.tsj` file formats)
6. mathematical tools: matrices ; vectors ; gradient noise functions (->procedural generation)
7. helper classes for coding roguelike or RPG games
8. helper classes for coding card games (Poker, Blackjack, *etc.*)
9. helper classes for adding artificial opponents/intelligent entities (NPCs) to your game

... It's only the beginning. More features will be added soon.

Also, it can be interesting to notice that the game engine PYV
is linked to an ecosystem of components,
that act in concert in order to make your life as a Game Dev more pleasant.

For instance, Kata.Games is a Gaming platform that will help indie game
developers from all around the globe (and especially PYV users) to create
and share digital experiences swiftly, super efficiently!

This platform should the first one that will share games created using PYV.



## 2. Get started

### Use pyv and create your first game

To install the Python package tied to PYV, simply type:
```shell
pip install pyved-engine
```

At this point, it's time to grasp an important concept:
__pyv__ is not constructed like the typical Python library.
Indeed, your source code shouldn't contain `import pyved_engine`
to link files directly.

Instead, __pyv__ ships with a dedicated command-line tool designed
for creating what one can name "game bundles".
A game bundle encompasses your game's source code, assets, relevant
metadata and also special code to execute game locally.

Consequently, your interaction with __pyv__ differs from how
you'd interact with a standard Python library, such as `pygame`.

When using __pyv__, you utilize commands to create a game bundle,
which can then be played.

Once __pyv__ is installed on your computer the initial steps involve
opening a command line and generating a new game.
To do so, type the following command:

```shell
pyv-cli init DemoGameBundle
```
That command initializes a new game bundle along with some
boilerplate source code. You will be prompted several questions, at this point
you can just press Enter at every step to keep default values.

Then, to verify that everything works as expected you would type:
```shell
pyv-cli play DemoGameBundle
```
In case no argument is provided to the subcommand play,
pyv assumes the current folder is a game bundle.
Of course, the name "DemoGameBundle" is just an example, you can name your
game bundle with any name you like.

### Customizing your game

... TODO ...

### Nota Bene for developers/contributors

If you are interested in testing the most recent features/
contribute to the development of the engine, rather than
installing the tool through the regular method, you should:
- clone the current repository
`git clone https://github.com/gaudiatech/pyved-engine.git`
- using the command line, navigate to the newly created folder on your hard drive, then install the package using the `pip` special mode "editable":
`pip install -e .`
In this way you'll be able to use the unstable (so-called
"bleeding edge") version instead of the Pypi stable version.

### Links to go further

[Platformer tutorial](https://gaudiatech.github.io/pyved-engine/GameTutorials/Platformer/)

[The official documentation](https://gaudiatech.github.io/pyved-engine/) (W-i-p)

[A linktree, to explore related sites](https://linktr.ee/katagames)



## 3. Misc

### Contribute

Everyone is welcome ; discussing ideas with the Python community more broadly
allows to enhance the design of PYV and to support Game Devs in the best
possible way!


Feel free to contribute to the projet if you wish to!

The documentation is built via the `mkdocs` tool. Feel free to improve it!

If you spot a bug, create an issue and tell everyone how to reproduce the bug!


You are welcome to contribute in this open-source project.
Newcomers are always treated with equity in our community.

The process is simple:
(a) start by forking `pyved-engine`,
 (b) Vreate your 1st Pull Request! Although not mandatory,
it's recommended but not mandatory to join our Discord server and discuss with
the community changes you would like to see/to add in the future.

Below are listed a few important
contributors –this is our Hall of fame.
* [moonbak](https://github.com/wkta) general architecture, event system, patterns: Mediator, MVC, ECS
* [tank-king](https://github.com/tank-king) game templates/various game demos (flappy bird, match3, clicker)
* [jwvhewitt](https://github.com/jwvhewitt) isometric engine
* ...

Acknowledgements:

* many thanks to Rik Cross for being an inspiration (ECS pattern)
* thank you Thorbjørn for providing indie game devs with an amazing tool (Tiled)

### License
Currently, materials in this repo are all licensed under the LGPL3 license.
See the `LICENSE` file for more info.
