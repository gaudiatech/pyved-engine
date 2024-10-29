# Project History

by Tom (thomas.iw@kata.games)


## Early period

- **Year 2017:**<br>
A first draft of a custom game engine written in Python was proposed as early as 2017.
Early names of the game engine, back when the source code was still rough and experimental,
have been forgotten.


- **August 2018:**<br>
An early version of the engine called `dingus2` has introduced the MVC pattern, and that
piece of software has been shared with two other game developers.
As far as I know, for the first time this engine has been used in a large-scale project (used for programming a python-based massively multiplayer game named *'Brutos Online'*)
Both projects (the game and the engine) were closed-source at that point.


- **April 2019:** <br>
In April 2019, the source code of the engine was made public (->open-sourced),
and that primitive game engine was dubbed `coremon_engine`.


## Period of exploration and discovery

- **May 2021:** <br>
I first experimented with using Brython to transpile a Pygame project in order to run
a video game in the browser, achieving promising results.
Then, I joined the dormant `brython-pygame` project and engaged with Brython’s creator,
Pierre Quentel. Unfortunately, he indicated that `brython-pygame` could not be restarted
as the original author was unreachable.


- **September 2021:** <br>
It became apparent that significant architectural changes were necessary to enable Python-based
games with full features like animations, sounds, and network communications to run in browsers.
This led to the conception of the `katasdk` library, an evolution of the earlier project.
Initial prototypes were shared on platforms like Reddit and Discord,
and a dedicated community channel was established on the Pygame Discord server.


- **March 2022:** <br>
After over a year of experimentation, I decided to segment the system into
multiple parts to enhance efficiency for end-users. Some components required 24/7 hosting
and data upload capabilities, leading to a subdivision of the project. The segment directly
utilized by game developers was named `kengi`. Simultaneously, we introduced a major update
in event processing by adopting a new event system that behaves like an overlay 
over the built-in Pygame system. The engine also included for the first time a few capabilities
for coding isometric games, significantly enhancing  the complexity of python games that can be
played in a browser


- **June 2022:** <br>
We attempted to integrate the kengi software into an experimental system with a 'metaverse'
component. To facilitate this, I linked a Stellar web wallet called 'Freighter,'
enabling the signing of transactions for depositing XLM. Another notable aspect
was our effort to embed the game editor directly within the metaverse itself.
This design was primarily inspired by *Roblox* and other massively multiplayer online games
that were extendable through custom scripting
(similar to the Ultima Online client paired with the RunUO server emulator).


- **December 2022:** <br>
The project has been partially funded, thanks to a grant from the Stellar Development
Foundation during the round #11 of the Stellar Community Fund. See [that link](https://communityfund.stellar.org/project/katagames).


- **April 2023:** <br>
The idea of a metaverse-like system was set aside as the kengi project evolved
into the project `pyved-engine`. We adopt a modular architecture and a more Pythonic approach
that relies heavily on the CPython base interpreter for the entire toolbox.
Since then, the pyved_engine has featured a new command-line interface for easier game prototyping
and a novel game format (game bundles), which together can significantly streamline
the game sharing process.


- **May 2023:** <br>
One month after letting go of the metaverse-like system, a new proof-of-concept is created.
The name "pyved" comes from *'Python Visual EDitor'*. Indeed, we now dream of a visual editor
for game developers, that would be easy to use, could take a low-code approach and would feature
a built-in level editor. Our first proof-of-concept relies on `pygame-ce` and `pygame-gui`.
That new component we prototyped would act as the GUI for using `pyved-engine` easily.


# Maturation period

- **June 2023:** <br>
We’ve brought the idea of launching game templates from the command line to life. Looking ahead,
we envision that this command-line tool could evolve significantly, empowering game developers in
unique and exciting ways to enhance productivity and streamline their workflow.


- **July 2023:** <br>
We're re-evaluating design patterns tied to `pyved-engine` and for a better gamedev API. We're 
re-considering the need of OOP (see [this commit](https://github.com/pyved-solution/pyved-engine/commit/1363d37572ab0d34905ab5d4fe953259e0da291e) for exmample)
This API needs a solid pattern to ensure scalability and ease of use. After testing various
options—such as Mediator, MVC, and a pure OOP approach with methods like `.update()` and `.draw()`.
We've recently experimented with a custom ECS (Entity Component System) pattern. The ECS
implementation is functioning well, providing a notable performance boost. However,
it remains uncertain whether this pattern will be adopted as the primary structure within
the gamedev API.


- **July 2024:** <br>
We’ve implemented a new network layer to streamline event sharing between client and server,
making multiplayer interactions more seamless. Using several mediators (one per software instance)
is feasible but still in an experimental state. After substantial effort, our first experiment
transpiling multiplayer code to Node.js using Transcrypt has been a success, paving the way
for more robust cross-platform capabilities in the future.


- **October 2024:** <br>
Repositories associated with our innovative game development solution have all been moved
to a new GitHub organization named `pyved-solution`. This transition paves the way for ambitious
future developments. Additionally, an older repository has been repurposed to store all game
templates, acting as an index. The `pyv-cli tool` now relies on this template index to initialize
new game prototypes.
