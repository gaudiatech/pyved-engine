<img src="https://gaudia-tech.com/shared/kengi-logo.png"/>
<p align="center">
<a href="https://discord.gg/nyvDpXebZB">join us on Discord<br>
<img alt="join us on Discord" src="https://img.shields.io/discord/876813074894561300.svg?label=&logo=discord&logoColor=ffffff&color=7389D8&labelColor=6A7EC2">
</a>
</p>

kengi is the abbreviation of **K**ata **ENGI**ne: a pythonic game engine built on top of
the in python built on top of the popular [pygame](https://github.com/pygame/pygame)
library. It has no other dependencies. So why "Kata"? [Kata.Games](https://kata.games) is
a new gaming portal for indie game fans!


## Get started
Using the command line, navigate to the `src` folder. To ensure that your python
distribution meets the requirements and to install the tool type:
```shell
> pip install -r requirements.txt
> pip install .
```
In this way, you can use `kengi` from any folder on your system. It is a good
practice to start all your games with this kind of code snippet:
```python
import katagames_engine as kengi
kengi.init('hd', caption='my first game')
pygame = kengi.pygame
```


## First demos
If you're familiar with `pygame`, getting used to `kengi` is really easy.
Navigate to the `src/` folder. There, you see a very basic example that uses only pygame:
* [demo-a-pygame.py](https://github.com/gaudiatech/kengi/blob/master/src/demo-a-pygame.py)

Now try to notice what is diffirent when one uses `kengi`, you see there are only minor
details that change:
* [demo-a-kengi-straightf.py](https://github.com/gaudiatech/kengi/blob/master/src/demo-a-kengi-straightf.py)

This is only one way to use `kengi` but it's most likely that you will start with this one,
if you already have some background in creating games using `pygame`.
Actually, one can see `kengi` as a mere wrapper around pygame. Everything that you can do
with `pygame` can be done the same way when using `kengi`, but `kengi` also unlocks
many new features that are very worthy of interest!

To explore more possibilites you can take a glimpse on the next demo
that implements the same thing but using the M-V-C pattern:
* [demo-a-kengi-mvc.py](https://github.com/gaudiatech/kengi/blob/master/src/demo-a-kengi-mvc.py)

Note that this program starts with the declaration
of a list of user-defined events. User-defined events can have attributes.
These events, just like regular pygame events, are processed via a standard method
`proc_event` that you need to re-define when you sub-class
`kengi.event.EventReceiver`...


## Game templates
Want to take a glimpse at how one would code a real game that has more features?
Having a basic set of game templates is a great thing for an engine,
since it allows you the user to bootstrap your next Game Dev project very fast!

So save yourself a lot of time for your project,
feel free to study/copy all files available in this folder:
* [game_templates](https://github.com/gaudiatech/kengi/blob/master/src/game_templates) 

To test a game template simply navigate the corresponding folder. There, type `python main.py`.
Game templates include a flappy bird clone... 

<img src="flappybird-preview.png" alt="flappybird screenshot" width=600>

Or a match3 puzzle game (screenshot below) and many other.

<img src="match3-preview.png" alt="match3 screenshot" width=600>


## Kengi design principles
1. Code layout matters. Clean, expressive code is not an option!

2. `kengi` is delivered along with 6 templates, see it as minimal examples of a real game.
A game template should be customizable very easily ;

3. `kengi` is based upon a custom event manager ;

4. `kengi` implements the M-V-C pattern.
People should be free to use this pattern or keep it basic based on their preferences.


## Goals
> "It’s Harder to Read Code than to Write it" - Joel Spolsky

The ultimate goal is to offer a mix of benefits for all
game devs who use python... These benefits are precious.
`kengi` enables you:

1. to write standardized therefore very easy-to-read code.
Readability is not to overlook!
If you take care of your code readability you'll encounter 30% less bugs,
you will fix any bug faster, etc. It works like magic!

2. to write a type of code that can evolve easily.
By using the built-in **custom event system** and the **M-V-C pattern**,
you can reach an amazing level of code flexibility.

3. to save a lot of time while creating your game

(And most importantly)

4. to use your `kengi`-based game  as the input for another 
tool that we produce, named `katasdk`.
This tool creates special game bundles, out of python source-code,
that can run in your browser! *A world premiere!*


## License
Currently, materials in this repo are all licensed under the LGPL3 license.
See the `LICENSE` file for more info.


## Contributors
When `kengi` becomes a great tool, we won't forget who made this
possible! Special acknowledgements:
* [tank-king](https://github.com/tank-king) wrote a great game template (flappy bird)
* ...

If you spot bugs, create an issue and tell us how to reproduce that bug.

The documentation is built via the `mkdocs` tool. Feel free to make it more user-friendly.
It's as simple as modifying a few text files in the `docs/` folder.

Fork `kengi`, Pull Requests are much appreciated! New contributors are always welcome. Thank you.
