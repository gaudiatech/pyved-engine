<p align="center">
  <img src="https://kata.games/pyv-logo.jpg" alt="pyv logo" />
</p>

Welcome to `pyved-engine`, a Python package bringing you *the most powerful and versatile
pythonic game engine for 2D games,* namely: **pyv**.

Designed to streamline and elevate your game development experience, **pyv** offers
a rich suite of tools tailored for rapid prototyping and smooth game creation.

<p align="center">
<a target="_blank" href="https://discord.gg/SHdJhcWvQD">
Consider joining our Discord server<br>
<img alt="join us on Discord" src="https://img.shields.io/discord/876813074894561300.svg?label=&logo=discord&logoColor=ffffff&color=7389D8&labelColor=6A7EC2">
</a>
</p>

<p align="center">
<big>A big Thank You! To our wonderful sponsors</big>
</p>

<table border="0" align="center">
<tr>
<td width="168" align="center">
<a href="https://stellar.org/foundation">
<img target="_blank" src="https://kata.games/img/sponsor1-logo.jpg" alt="Stellar Development Foundation logo" width="80" height="80"></a><br>
<sub>Stellar Development Foundation</sub>
</td>
<td width="168" align="center">
<a target="_blank" href="https://kata.games">
<img src="https://kata.games/img/sponsor2-logo.png" alt="KataGames Startup logo" width="80" height="80"></a><br>
<sub>The KataGames Startup</sub>
</td>
<td width="168" align="center">
<img src="https://kata.games/img/sponsor3-logo.jpg" alt="Sponsor 3 logo" width="80" height="80"><br>
<sub>Future Sponsor</sub>
</td>
</tr>
</table>

## 0. Is this tool for me?
Game engines offer valuable time-saving benefits by providing a framework with reusable code.
With pyv, skip the hassle of reinventing the wheel and quickly implement essential
game features like pathfinding and spritesheet loading.

Our custom engine empowers you
to create captivating, bug-free games, with built-in modules for asset management,
AI, procedural generation, and more—the only limit is your imagination!

Whether you're crafting your first game
or refining your latest masterpiece, **pyv** is here to unlock new possibilities,
turning your ideas into immersive, playable worlds!
With **pyv**, you gain the productivity-boosting perks of a game engine
designed for modern 2D game development. No more building from scratch!

**pyv** is a framework packed with reusable and customizable
code snippets, empowering you to focus on what matters most: **your game's unique vision**.


## 1. Getting started

The simplest way to install the toolbox is to type:
```shell
pip install pyved-engine
```

At this point, it's time to grasp an important concept: for reasons that will become clear
only later, __pyv__ is not built in the same way other typical Python libraries are built.

Indeed we have set a special rule:

Your game's source-code **should NEVER contain** the following line:
```python
import pyved_engine
```
This would link your source-code directly to the library and would not allow us to
use advanced features that will be described later on.

Consequently, interacting with __pyv__ differs from what you may see with other libraries
such as `pygame` for example. Instead of using import instructions, __pyv__ ships with a dedicated *command-line tool* designed
to manipulate what we refer to as "game bundles".

You access the *command-line tool* from a terminal, via
the keyword `pyv-cli`.

A game bundle encompasses your game's source code, assets, but also relevant
metadata. It also contains a generic script that executes game in the local context.

To sum up, when using __pyv__ you should interact with game bundles always
through the *command-line tool*.
To test the idea, open a terminal, and type:

```shell
pyv-cli -v
```
This prints out the version and lets you know your `pyved-engine` installation is Ok.

#### Important remark for Linux users
In case you have installed `pyved-engine` only for the local user, and
the `pyv-cli` command seems to be missing,
you would need to update your PATH variable by hand! To do so:
`export PATH=~/.local/bin:$PATH`


## 2. Game templates

The framework that comes with `pyved-engine` relies on ideas such as *game bundles*,
and *game templates*. Your creation is packed inside a game bundle. And you never
create a bundle *ex nihilo*/ from nothing. Instead, you select a game template
(some game templates can be very empty, tho) and you customize it.

#### Create your very first game

In order to create a new game bundle, you can type:

```shell
pyv-cli init myFirstDemo
```

What the `init` sub-command does is initializing a new game bundle,
it will add some boilerplate source-code, placeholder-like files,
all being based on a game template you can select freely.

When prompted what game template you wish, we recommend to select the "ROGUE LIKE" as this is
an interesting example, yet not too complex one.

When prompted other questions (that are not mandatory) you're free
to *press Enter* at every step. In that way, the tool keeps default values.

#### Running your game
After the game bundle initialisation step, to verify that everything went well,
let us type:
```shell
pyv-cli play myFirstDemo
```
It is mandatory to provide an argument for the `play` sub-command.

Of course, the name "myFirstDemo" is a mere example, you are free to name your
game bundle with almost any name you like.

## 3. Sharing games

The most unique feature our toolbox provides you with,
is the ability to *easily share your python-based game through the web*!

You can test that this principle works, by loading the following webpage in your browser:<br>
[https://pyvm.kata.games/play/tfinalise](https://pyvm.kata.games/play/tfinalise).

In order to share an existing game bundle, you can use the dedicated sub-command:
```
pyv-cli share myFirstDemo
```

A possible result is shown via the screenshot below:<br>
![Shared game](shared.game.png?raw=true "Example of shared game")


#### Remark
Note that the game identifier (in our system, this is sometimes called 'slug') must be unique.
If your game identifier is already used server-side, you will need to rename your game bundle.
This is handled automatically (interactive behavior in the terminal after running `pyv-cli share`).

## 4. Some theory

#### Vision and goals behind pyv

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

#### How do Pyv and Pygame differ, precisely?

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

#### Details about our engine's features

The __pyv__ engine comes packed with a ton of features:

1. event queue (simplifies the use of patterns such as: Mediator, the MVC pattern)
2. gamestate stack, state management via events 
3. simple GUI creation: buttons, checkboxes, *etc.* 
4. tileset loading, sprite animation
5. tilemap parser (based on `.tmx` or `.tsj` file formats)
6. mathematical tools: matrices ; vectors ; gradient noise functions (->procedural generation)
7. helper classes for coding roguelike or RPG games
8. helper classes for coding card games (Poker, Blackjack, *etc.*)
9. helper classes for adding artificial opponents/intelligent entities (NPCs) to your game

More features will be added in the future.

Also, it can be interesting to notice that the game engine __pyv__
is linked to an ecosystem of components,
that act in concert in order to make your life as a Game Dev more pleasant.

For instance, Kata.Games is a Gaming platform that will help indie game
developers from all around the globe (and especially __pyv__ users) to create
and share digital experiences swiftly, super efficiently!

This platform should the first one that will share games created using __pyv__.


## 5. Modifying a game bundle

Example of metadata:
```
{
    "vmlib_ver": "24_9a3",
    "dependencies": {
        "pyved_engine": [
            "24_9a3",
            "pyv"
        ]
		},
    "description": "experimental game",
    "author": "Thomas",
    "asset_list": [
    ],
    "asset_base_folder": "my_folder",
    "sound_base_folder": ".",
    "sound_list": [],
    "slug": "SuperProj",
    "title": "Untitled Game",
    "thumbnail512x384": "thumb_2.png",
    "thumbnail512x512": "thumb_1.png",
    "ktg_services": false,
    "instructions": "not provided",
    "uses_challenge": false,
    "has_game_server": false,
    "ncr_faucet": false,
    "game_genre": [
        "Experimental",
        "Arcade"
    ],
    "game_title": "SuperProj",
    "build_date": "Tue Oct 22 20:11:29 2024",
    "source_files": [
        "gamedef.py",
        "shared.py",
        "systems.py",
        "world.py",
        "__init__.py"
    ]
}
```
...TODO...

That part needs some more work.
You can refer to our
[work-in-progress documentation](https://pyved-solution.github.io/pyved-engine/).

Many game engine features are well described there.


#### To go further

[Platformer tutorial](https://pyved-solution.github.io/pyved-engine/GameTutorials/Platformer/)

[The official documentation](https://pyved-solution.github.io/pyved-engine/) (W-i-p)

[A linktree, to explore related sites](https://linktr.ee/katagames)


## 6. Contribute

*Everyone is welcome to join our developer team!*

If you are interested in testing the most recent features/
contribute to the development of the engine, rather than
installing the tool through the regular method, you should:

- clone the current repository via a:
`git clone https://github.com/pyved-solution/pyved-engine.git` command ;<br><br>
- use the command line to navigate to the newly created folder on your hard drive,
then install the lib but using the `pip` special mode "editable mode":
`pip install -e .`<br><br>
-in this way you are able to use the unstable (so-called
"bleeding edge") version, modify it an see how your changes impact the tool in real time.

#### Improving the documentation
Discussing ideas with the Python community more broadly
allows to enhance the design of __pyv__ and to support Game Devs.

The documentation is an important part of that effort.
Our documentation is built via the `mkdocs` tool. Feel free to read about
mkdocs [here](https://realpython.com/python-project-documentation-with-mkdocs/),
and improve the __pyv__ documentation that you can find in the [docs folder](docs/)

#### Issues

If you spot a bug, create an issue and tell everyone how to reproduce the bug.
We will try to solve it as soon as possible.
You are welcome to comment in this open-source project.
Newcomers are always treated with equity in our community.

#### Pull requests

Pull requests are welcome.

To create a pull request:
 (a) start by forking the repository `pyved-engine`,
 (b) Create your 1st Pull Request! Although not mandatory,
it's recommended but not mandatory to join our Discord server and discuss with
the community changes you would like to see/to add in the future.


#### Acknowledgements:

* many thanks to Rik Cross for being an inspiration (ECS pattern)
* thank you Thorbjørn for providing indie game devs with an amazing tool (Tiled)

Below are listed a few important
contributors –this is our Hall of fame.
* [moonbak](https://github.com/wkta) general architecture, event system, patterns: Mediator, MVC, ECS
* [tank-king](https://github.com/tank-king) game templates/various game demos (flappy bird, match3, clicker)
* [jwvhewitt](https://github.com/jwvhewitt) isometric engine
* ...

## 7. License
Currently, materials in this repo are all licensed under the LGPL3 license.
See the `LICENSE` file for more info.
