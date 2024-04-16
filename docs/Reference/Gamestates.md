
### About gamestates

When your game starts to be complex, this will require you to use what
is known as 'Gamestates'.

A game state is a mode in the game that is relatively independant from other modes.
It uses a view and a set of actions that the user can perform.

For example, it many games you will find a **Title screen**, where controls
are different from controls you will find in the game itself (if it is an action game, in the game itself you will
shoot enemies, whereas in the *Title screen* you only select options)

### Declare your game states

You will need a file where you declare all your gamestates, like this:

``` py
# import ok for development mode
import pyved_engine as pyv

# in production mode, its recommended to use:
# from . import pimodules
# pyv = pimodules.pyved_engine

pyv.declare_game_states(GameStates, {
    GameStates.TitleScreen: MyStateA,
    Gamestates.Shooter: MystateB
})
```

... But before that, the variable `GameStates` needs to be defined such as:
``` py
GameStates = pyv.e_struct.enum(
    'TitleScreen', 'Shooter'
)
```
Values found in the dictionary passed to `declare_game_states` are classes
that inherit from the engine's core class `BaseGameState`, for example:

``` py
class PuzzleState(pyv.BaseGameState):
    def __init__(self):
        # your custom code goes there
        pass

    def enter(self):
         # your custom code goes there
        pass
    
    def release(self):
        # your custom code goes there
        pass
```
