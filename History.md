# Project History

by Tom (thomas.iw@kata.games)


## Early period

- **April 2019:** <br>
A first draft of a custom game engine written in Python was proposed as early as 2017.
The early names of the game engine, when the source code was still closed-source,
have been forgotten. However, in April 2019, the source code of the engine was released,
and that primitive game engine was dubbed coremon_engine.


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
in event processing by adopting a custom event system over the built-in Pygame system.
This update also included capabilities for coding isometric games, significantly enhancing
the complexity of games that could be run in browsers.


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
into the pyved_engine, adopting a modular architecture and a more Pythonic approach
that relies heavily on the CPython base interpreter for the entire toolbox. Since then,
the pyved_engine has featured a new command-line interface for easier game prototyping
and a novel game format (game bundles), which together significantly streamline
the game-sharing process.
