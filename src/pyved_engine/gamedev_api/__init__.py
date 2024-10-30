"""
Tom said: in a perfect world the gamedev_api should be structures like this:

 - __init__: stores the list of all functions and classes that concretize the API
   (it should be obvious that this file's sole purpose is to select objects from engine_logic, as well as
   objects from highlevel_func and expose them nicely)

 - highlevel_func: implementations that exist at a such high level of abstraction that the ctx doesnt matter
 - context_bridge: basically a container for implementations that can be replaced, based on the ctx
   (->dependency injection pattern)

 - engine_logic: stores the general state of the engine, how the engine transitions from 1 state to another, etc.
   (functions such as init are defined here because they indeed modify the engine state. This file imports the
   two modules mentionned above)
"""
# TODO refactoring
