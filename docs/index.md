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
By definiing many useful [features](##Engine features) as described in the next section.

!!! warning
    The engine **Pyv** is an ambitious and still experimental project. Do not consider anything you see here
	as production-ready. Instead, we hope to receive some help from the community of open-source fans.
	If you spot bugs please go to our GitHub page and at leaste create an Issue! Explain how to reproduce the bug.
	If you have some spare time, you may fork the project then improve the tool. Pull requests are very welcome!


## Select an architecture/a pattern for your game

Design patterns are crucial to be effective in game development.

In the context of `pyv`, you can select one out of three design patterns:

- [Mediator](<Other patterns\Event based programming.md>) : this solution is the more flexible. It offers centralized event
manager object that will simplify object communication, and you can basically work as you prefer.
<br><br>

- As of today (november 2024) The [Actor based pattern](<ActorBasedPattern.md>) is the recommanded gamedev API,
for newcomers and testers of the **Pyv** solution. 

- ECS : the [Entity Component System](<Entity Component System\A bit of theory.md>) ;
if you want to directly review some code examples you can go to
[ECS Examples](<Entity Component System/ECS examples.md>)
<br><br>

- MVC : the [Model-View-Controller pattern](<Other patterns\MVC Examples.md>) is a more strict
variant of the Mediator.

Please go to the dedicated page, and start learning  more about the design pattern you plan to use!


## Engine features

To conclude this overview, 
we provide you with a list of the ton of features, the game engine **Pyv** comes packed with.

- **Event queue** (simplifies the use of patterns such as: Mediator, the MVC pattern)
- **Design patterns** (Such as : **Mediator, Actor-based, ECS, and MVC**)
- **Gamestate stack**, state management via events
- **Simple GUI creation**: buttons, checkboxes, etc.
- **Tileset loading**, sprite animation
- **Tilemap parser** (based on .tmx or .tsj file formats)
- **Mathematical tools**: matrices ; vectors ; gradient noise functions (->procedural generation)
- **Helper classes for multiple types of games** : Roguelike, RPG games, Card games (Poker, Blackjack ...).
- **Helper classes for adding artificial opponents/intelligent entities** (NPCs) to your game
- **Isometric 3D game engine** 
- **Ease of distribution** (Our platform KataGames will help deploy the game and make it playable through a browser in seconds)
- **Helper classes to create stories**
- **Helper classes to generate terrain randomly** (level generation, etc.)


## Results

All ideas presented above will allow you to create a great variety of games without too much trouble!

Below, you can see some screenshots of game created using **Pyv** in a very short period of time.

![Game examples](./images/gallery2.png "Games")

!!! tip
    There are numerous examples of games that you can see in the [Showcase page](<Showcase.md>) !
    To inspect source-code of many sample/experimental games, you may visit: <https://github.com/pyved-solution/game-templates-index> this is an amazing
	and rich source of information for any new developer to **Pyv**

*This is only the beginning!*

More features will be available before 2025, and many more games are expected to appear early in 2025.
Maybe the next fantastic **Pyv**-based game will be created by you?!