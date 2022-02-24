
<img src="https://gaudia-tech.com/shared/kengi-logo.png"/>

<p align="center">
<a href="https://discord.gg/nyvDpXebZB">join us on Discord<br>
<img alt="join us on Discord" src="https://img.shields.io/discord/876813074894561300.svg?label=&logo=discord&logoColor=ffffff&color=7389D8&labelColor=6A7EC2">
</a>
</p>

"kengi" is the abbreviation of <ins>K</ins>ata.Games <ins>ENGI</ins>ne.

It's a game engine fully written in python, built on top of the popular
[pygame lib](https://github.com/pygame/pygame) and with almost no other
dependencies.

Kata.Games is the name of a new gaming portal that aims at distributing
newly created browser games. You can test the
[pre-alpha version of this portal](https://kata.games) if you're curious!


## Contributions
Feel free to contribute and improve the game engine.

If you spot bugs, please create an issue and
tell us how to reproduce that bug.
Pull requests are welcome.
Documentation is built via the `mkdocs` tool
(see `docs/` for sources).
Improving the docs is as important as improving the code!

Any kind of help is very appreciated!

Discord if you wish to discuss with current contributors.


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


## Get started
See the file `requirements.txt` to learn about dependencies.

To start using the engine, clone this repo then copy-paste the whole
`src/katagames_engine`
inside the `sources/` or `src/` folder of your own game project.

If you plan to use the engine alone,
it is recommended that you tie your code to the lib via:
```
import katagames_engine as kengi
```

In case you wish to use the engine along with `katasdk`,
the installation is a bit different and the recommended syntax changes.
For example:
```
# - katasdk+kengi, the general case -
import katagames_sdk as katasdk
kengi = katasdk.import_kengi()
```
Please refer to [the KataSDK official documentation](https://kata.games/developers)
to know everything about this use case.

## Mini-tutorial
...todo...

## Graphic modes
...todo...

## License
Materials in this repo are licensed under the LGPL3 license,
see `LICENSE` file.
