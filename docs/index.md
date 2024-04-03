# Introduction


## Introduction to Pyved Engine

The Pyved engine, or **PYV** for short,

is the name of a game engine fully written in python.

**PYV** is more or lesse a wrapper around the popular `pygame` library.

If you have some prior experience developing games with `pygame`,
transitioning to **PYV** should be quick and relatively easy.


### Why PYV?

Confusion appears to exist within the community regarding the differentiation
between a Python package, and a game engine.

It's crucial to understand that although Pygame functions as a regular
Python package/library, it doesn't provide the extensive array of features present in a
specialized 2D game engine!

Consequently, it might not satisfy all the
prerequisites essential for the development of a fully-realized game.

With PYV we wish to create a new standard for python game development,
adding new features and
possibilities.


### Our ultimate goals

- The primary goal of PYV is to elevate the accessibility, learnability,
and overall experience of Python game development to new heights.


- In the long-term, with PYV we aspire to elevate Python game development
by ensuring it becomes easier to use, easier to learn, reliable and a source of economic growth
for many individuals.

How to accomplish this?
By definiing many useful [features](#Engine features) as described in the next section.


## Engine features

The game engine comes packed with a ton of features:

- **Design pattern** (Such as : **ECS, Mediator and MVC**)
- **Event queue** (simplifies the use of patterns such as: Mediator, the MVC pattern)
- **Gamestate stack**, state management via events
- **Simple GUI creation**: buttons, checkboxes, etc.
- **Tileset loading**, sprite animation
- **Tilemap parser** (based on .tmx or .tsj file formats)
- **Mathematical tools**: matrices ; vectors ; gradient noise functions (->procedural generation)
- **Helper classes for multiple types of games** : Roguelike, RPG games, Card games (Poker, Blackjack ...).
- **Helper classes for adding artificial opponents/intelligent entities** (NPCs) to your game
- **Isometric 3D game engine** 
- **Ease of distribution** (Our platform KataGames will help deploy the game and make it playable through a browser in seconds)

...And this is only the beginning.

More features will be available soon.

![Game examples](./images/gallery2.png "Games")

**You can checkout other examples of the games we did in the [Showcase page](<Showcase.md>)**  


## An architecture for your game

We mentioned design patterns before. In the context of `pyv`,
you can select one out of three design patterns:

- ECS : the [Entity Component System](<Entity Component System\A bit of theory.md>) ;
if you want to directly review some code examples you can go to
[ECS Examples](<Entity Component System/ECS examples.md>)
<br><br>

- [Mediator](<Other patterns\Event based programming.md>) : this solution uses a centralized event manager object that will simplify object communication
<br><br>

- MVC : the [Model-View-Controller pattern](<Other patterns\MVC Examples.md>) is a more strict
variant of the Mediator.

Please go to the dedicated page to learn more about the design pattern you plan to use.
