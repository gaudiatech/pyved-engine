# PYVED ENGINE

## Introduction

**PYV** is the name of a game engine fully written in python.

It's a wrapper around the popular `pygame` librabry, therefore if you have some prior experience with developing games with `pygame`, transitioning to **PYV** should be extremely easy!

### Why Pyved

Confusion appears to exist within the community regarding the differentiation between a Python package, and a game engine.

It's crucial to understand that although Pygame functions as a regular Python package/library. It doesn't provide the extensive array of features present in a specialized 2D game engine! Consequently, it might not satisfy all the prerequisites essential for the development of a fully-realized game.

Pyved wants to create a new standard for python game development adding new features and possibilities, everything will be detailed into the [features](#features) section.

### Goals

- **Objective**: The primary objective of PYV is to elevate the accessibility, learnability, and overall experience of Python game development to new heights.

- **Aspiration**: PYV aspires to elevate Python game development by ensuring it becomes easier to use, easier to learn, and more reliable.

But how a *simple pygame wrapper* will do this ?

## Features

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

... It's only the beginning. More features will be added soon.

### Galery
![Game examples](./images/galery1.png "Games")
![Game examples](./images/galery2.png "Games")


![The breakout end result](<./Game Tutorials/img/breakoutend.png> "breakout")
![The patformer end result](<./Game Tutorials/img/screenshot.png> "Our platformer")


## Game architecture 

We mentionned designs pattern before, let's make a brief summary here, but you can find more details in the relevant pages.

### ECS : Entity Component System

The ECS pattern is a recent industry standard for game development, it's concept is to decompose game entities into "bricks" kind of like legos, so you can assemble things in a easier way and avoid confusion.

Read more in the [ECS](<Entity Component System\A bit of theory.md>) section.



![ECS](./images/ECSBlockDiagram.png "ECS Diagram")

credit : https://docs.unity3d.com/Packages/com.unity.entities@0.1/manual/ecs_core.html 

### Mediator 

In the realm of game development, the Mediator Pattern serves as a crucial architectural concept. Think of it as the bridge that connects various game elements and entities, allowing for seamless interaction. Much like assembling game components into a cohesive whole, the Mediator Pattern simplifies the orchestration of complex systems, ensuring smoother gameplay and reduced confusion.

![Mediator](./images/mediator.webp "Mediator diagram")

credit : https://medium.com/@andrewMacmurray/exploring-the-mediator-pattern-eadaebc871b4

### MVC

MVC, or Model-View-Controller, is a foundational architectural pattern that has long been a cornerstone in software development. It divides an application into three interconnected components: Model, View, and Controller. Much like separate pieces of a well-organized puzzle, these components work in harmony to create a structured and efficient software system.


![MVC](./images/mvc1.ppm "MVC diagram")

credit : https://www.researchgate.net/publication/342748612_Zetcil_Game_Mechanic_Framework_for_Unity_Game_Engine


![MVC](./images/mvc.jpg "MVC diagram")


credit : https://www.technoarchsoftwares.com/blog/mvc-framework/





