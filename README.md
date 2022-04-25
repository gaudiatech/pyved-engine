
<img src="https://gaudia-tech.com/shared/kengi-logo.png"/>

<p align="center">
<a href="https://discord.gg/nyvDpXebZB">join us on Discord<br>
<img alt="join us on Discord" src="https://img.shields.io/discord/876813074894561300.svg?label=&logo=discord&logoColor=ffffff&color=7389D8&labelColor=6A7EC2">
</a>
</p>

kengi is the abbreviation of **K**ata game **ENGI**ne; a game engine written in python built on top of the popular
[pygame](https://github.com/pygame/pygame) library. It has no other dependencies.

But why Kata? [Kata.Games](https://kata.games) is a new gaming portal (it's already online so test it if you're curious!)
that aims at distributing cool indie games.

## Getting started
Using the command line, navigate to the `src` folder. Ensure that you meet the requirements,
by typing:
```shell
> pip install -r requirements.txt
```
Then you can run minimalistic examples by typing:
```shell
> python min-example-kengiOn.py
```
or
```shell
> python min-example-gui.py
```

In order to create your own games or run better examples, you have to install the tool.
Hence you can use `kengi` from anywhere on your system.
Navigate to the `src` folder if you haven't done so before and type this command:
```shell
> pip install .
```

If you really prefer to test the tool before installing,
you can always copy-paste the whole
`src/katagames_engine` folder into your own project.
This works too but you would have to do this for every program.

## Basic tutorial
If you already know how to code games in `pygame`, transition to `kengi` is super easy!
There are only 6 new lines to be aware of.
Count with me to six, *I promise it's worth your time*.

The import and three initialisation steps:
```python
import katagames_engine as kengi
kengi.init('hd')  # instead of pygame.init(), and pygame.display.set_mode(...)

pygame = kengi.pygame  # alias to keep on using pygame, easily
screen = kengi.core.get_screen()  # new way to retrieve the surface used for display
```
You see? 4/6, woohoo! We're almost done.

In the game loop you will need to update the display every frame:
```python
kengi.flip()  # instead of pygame.display.flip(), for example
```
And lastly at the end of your program you need to call:
```python
kengi.quit()  # instead of pygame.quit()
```
And voila! You are now a `kengi` user, congrats.


## Background
The story behind `kengi` starts back in july 2018.

After coding several small games
I was surprised by the productivity boost you can get,
if you introduce a few particular patterns. It led me to study game engines and experiment.

While you can be surprised by some details found in the code,
the code layout isn't random at all.
If you know better solutions about how to solve game dev problems using python,
we want to hear about you!

The ultimate goal is to offer a unique mix of benefits for all
game devs using python... Benefits you don't see elsewhere.

## Game Engine benefits
What is so good about `kengi`? It enables you:

1. to create games much faster

2. to write standardized, therefore easy-to-read code.
Encounter at least 30% less bugs, fix bugs faster...
It's like magic!

3. to write code that evolves easily.
By using the included M-V-C pattern, you can reach a level of code flexibility
that is amazing 

And the most important one:

if used along with another component named `katasdk`, the `kengi`
is the first *pygame-based* Game Engine that produces browser games!
*A world premiere!*

## Design principles

1. Code layout matters. Clean, expressive code isn't optional ;

2. `kengi` is delivered along with 5 templates, see it as minimal examples of a real game.
A game template can be adjusted to your needs easily ;

3. `kengi` is based upon a custom event manager ;

4. `kengi` includes classes that implement the M-V-C pattern.
You are free to use the pattern in your games or keep it basic, as you wish.

> "It’s Harder to Read Code than to Write it" - Joel Spolsky


## Targeting the browser
In case you wish to use the engine along with `katasdk`,
the installation is a bit different and the recommended syntax changes.
For example:
```
# - katasdk+kengi, the general case -
import katagames_sdk as katasdk
kengi = katasdk.import_kengi()
```
Please refer to [the KataSDK official documentation](https://kata.games/developers)
to learn more about this scenario.


## License
Materials in this repo are licensed under the LGPL3 license,
see `LICENSE` file.


## Contribute
Feel free to contribute and improve the game engine.
If you spot bugs, please create an issue and
tell us how to reproduce that bug.
Pull requests are welcome.
Documentation is built via the `mkdocs` tool
(see `docs/` for sources).
Improving the docs is as important as improving the code!
Any kind of help is very appreciated!
Discord if you wish to discuss with current contributors.


## Graphic modes
...todo...
