# The kengi project
kengi? The abbreviation of <ins>K</ins>ata.Games <ins>ENGI</ins>ne.

[Kata.Games](https://kata.games)? The name of a new gaming portal.
Test it out if you're curious!

More precisely `kengi` is a game engine fully written in python,
and it is a wrapper around the popular 
[pygame lib](https://github.com/pygame/pygame).


## Contributions
Feel free to contribute!
If you spot bugs, please create an issue and
tell us how to reproduce that bug.

Pull requests are welcome.
Documentation is built via the `mkdocs` tool
(see `docs/` for sources).
You can improve the docs if you prefer to write in plain english, not in python!

Any kind of help is very appreciated.

Join the [Discord server](https://discord.gg/nyvDpXebZB)
to receive news about the dev/ if you need help for your game dev based on `kengi`.


## Background
The story behind `kengi` started back in july 2018 when I got serious about
coding games in python. While you can be surprised by some details found in the code, 
you can be sure that the software design isn't random at all.

If you know better solutions about how to solve game dev problems,
using python, we want to hear about you!

I've studied many game engines but I wanted to propose one
that has a unique mix of benefits... Benefits not seen elsewhere.


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
1. `kengi` is delivered along with 5 templates, see it as minimal examples of a real game.
A game template can be adjusted to your needs easily

2. `kengi` is based upon a custom event manager

3. `kengi` includes classes that implement the M-V-C pattern.
You are free to use the pattern in your games or keep it basic, as you wish

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
