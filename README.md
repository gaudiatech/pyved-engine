<p align="center">
  <img src="https://gaudia-tech.com/shared/pyv-logo.jpg" alt="pyv logo" />
</p>

Introducing `pyved-engine`, a Python package that provides you with
our powerful and efficient 2D game engine named __pyv__.
Designed to streamline game development, __pyv__ offers a comprehensive set of
tools for rapid prototyping and game production. Don't wait any longer,

<p align="center">
<a href="https://discord.gg/SHdJhcWvQD">
Click here to join our vibrant Discord community<br>
<img alt="join us on Discord" src="https://img.shields.io/discord/876813074894561300.svg?label=&logo=discord&logoColor=ffffff&color=7389D8&labelColor=6A7EC2">
</a>
</p>

Do yourself a favor: unlock the full potential of your game development thanks to __pyv__!



## 1. Introduction

### What's the deal about Pygame?

Pygame is an amazing library, that being said, confusion appears to exist
within the community regarding the differentiation between a Python package,
and a game engine.

It's crucial to understand that although Pygame functions as a decent
Python package, it doesn't provide the extensive array of features present
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

### Unveiling the capabilities of a game engine

A game engine provides invaluable time-saving benefits by storing a collection
of useful and reusable code snippets within its framework.
Instead of reinventing the wheel and wasting your precious time by re-writing
generic code for video games, you can leverage the power of the engine.

By referring to the comprehensive documentation, you can quickly learn how to
implement various functionalities such as pathfinding or loading spritesheets.
With simple function or method calls, you can seamlessly integrate these
features into your game, saving precious development time and effort!

Create captivating and bug-free applications effortlessly. __pyv__ offers an
array of built-in modules for seamless management of game assets, AI integration,
procedural generation, and other advanced features.


### Specific goals
As a wise man said:
> "It’s Harder to Read Code than to Write it"\
> — Joel Spolsky

Our general goal is to empower you to:

* __Write standardized therefore very easy-to-read code__:
readability is not to overlook! If you take care of your code readability you'll
encounter 30% fewer bugs, you will fix any bug faster, etc. It works like magic!
* __Write a type of code that can evolve easily__: by using our *built-in event
system* along with the *M-V-C pattern*, you can reach a high level of code
flexibility.
* __Be more productive__
* __Distribute your newly created games__ via the new awesome
[https://kata.games](https://kata.games) platform!

In this way, your Python game can be played directly 
in any modern browser (Chrome, Brave, *etc*): a world premiere!

### Other details

Why "kata"?
[Kata.Games](https://kata.games) denotes a new gaming platform that helps indie game developers to create and share
digital experiences easily, all around the globe!
Via this innovative platform, we're proud to publish all kinds of games powered by `pyved-engine`.

About the list of planned features... The game engine already comes
packed with a ton of features:

1. global event queue (simplifies the use of both the Mediator and the MVC design patterns)
2. gamestate stack, state management via events 
3. simple GUI creation: buttons, checkboxes, *etc.* 
4. tileset loading, sprite animation
5. tilemap parser (based on `.tmx` or `.tsj` file formats)
6. mathematical tools: matrices ; vectors ; gradient noise functions (->procedural generation)
7. helper classes for coding roguelike or RPG games
8. helper classes for coding card games (Poker, Blackjack, *etc.*)
9. helper classes for adding artificial opponents/intelligent entities (NPCs) to your game

...More will be added in the future.

## 2. Get started

### Use pyv and create your first game

To install our Python package, simply type:
```shell
pip install pyved-engine
```

At this point, it's crucial to grasp an important concept:
__pyv__ is not constructed like a typical Python library.
Indeed, your source code won't directly import `pyved_engine`...

Instead, __pyv__ ships with a dedicated command-line tool designed
for creating what we refer to as "game bundles".
A game bundle encompasses your game's source code, assets, and relevant
metadata. Consequently, your interaction with __pyv__ differs from how
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

### Customize your game

... TODO ...

### Links to learn more about the project

[The official documentation](https://gaudiatech.github.io/pyved-engine/) (W-i-p)

[A linktree, to explore our medias](https://linktr.ee/katagames)


## 3. Misc

### Contribute

Feel free to join the developer team. It's a super easy two-step process:
(a) start by forking `pyved-engine`,
 (b) join our Discord to talk with us and create your 1st Pull Request!

If you spot a bug, create an issue and tell us how to reproduce the bug.
The documentation is built via the `mkdocs` tool. Feel free to use it.

Newcomers are always welcome. Below are listed a few important
contributors –this is our Hall of fame.
* [wkta-tom](https://github.com/wkta) architecture, event system, design patterns
* [tank-king](https://github.com/tank-king) fancy game templates (flappy bird, match3)
* [jwvhewitt](https://github.com/jwvhewitt) isometric engine
* ...

### License
Currently, materials in this repo are all licensed under the LGPL3 license.
See the `LICENSE` file for more info.
