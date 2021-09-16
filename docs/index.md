# The Kata.games SDK

SDK stands for Software Development Kit. This is a set of tools for third-party developers who wish to produce games that target the [Kata.games platform](https://kata.games). If you require further assistance you can always reach out to our friendly Support Team, via e-mail: [support@kata.games](mailto:support@kata.games).

## Overview

KataSDK is made up of four parts:

* a game engine written in Python, named `kataen`
* a pygame emulator able to run pygame programs in the web context
* an API, named `katapi` that is useful for interacting with our servers
* a set of commands that helps you in publishing/ pushing games to our platform

## Main project files

	mkdocs.md          # meta-informations for the current Doc.
    README.md          # projet description
	
	docs/              # sources(Markdown) of pages making up the current Doc.
	
    examples/
	    microinvader/  # minimal game that uses keyboard events
		mouse_test/    # how to catch mouse events
        sound_test/    # how to use sound effects
	
	katagames_sdk/     # source(Python) of the various SDK parts
	scripts/           # source(Javascript) of Web-related components