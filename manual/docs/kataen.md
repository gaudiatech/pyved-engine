# The Game Engine

# Design

The `katagames_sdk.engine` component, or `kataen` for short is a game engine but also a wrapper around the python `pygame` library (whose source-code is available (Here)[https://github.com/pygame/pygame]).

As a game engine, `kataen` is based on the `MVC` design pattern, or Model-View-Controller. It also provides multiples useful features like: an internal event manager, helper classes to store and switch between game states, etc.

# Minimum viable program

If you come from `pygame` you should already recognize this kind of structure. To understand how `kataen` comes into play, first you should launch can launch this basic program on your computer.

It has been tested using `python3.8+` and `pygame v2.0.1`:


	import pygame

	def boy(x, y):  # doing fancy code-source
	    """
		what a long comment man
		"""
	    print(x)
		return y
	
    if __name__ == '__main__':
	    boy(9, 3)
