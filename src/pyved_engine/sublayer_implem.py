
from abc import ABC, abstractmethod


# Step 1: Define an interface (abstract class)
from pyved_engine.custom_struct import Objectifier


class GameEngineSublayer(ABC):
    """
    this is used solely to specify the full interface of the Gamedev API

    goal of this CLASS is to define the full engine API for end users...
    But also specialize the API implementation based on the exec. context
    Tom said: in a perfect world the API for the gamedev should be structured ,
     like in FOUR(4) files or parts :

     - I- part
      stores the list of all functions and classes that concretize the API
       (it should be obvious that this file's sole purpose is to select objects from engine_logic, as well as
       objects from highlevel_func and expose them nicely)

     - highlevel_func: implementations that exist at a such high level of abstraction that the ctx doesnt matter

     - context_bridge: basically a container for implementations that can be replaced, based on the ctx
       (->dependency injection pattern)

     - engine_logic: stores the general state of the engine, how the engine transitions from 1 state to another, etc.
       (functions such as init are defined here because they indeed modify the engine state. This file imports the
       two modules mentionned above)
    """
    @abstractmethod
    def fire_up_backend(self, user_id: int) -> dict:
        """Fetch user data"""
        pass

    @abstractmethod
    def draw_line(self, *args, **kwargs):
        pass

    @abstractmethod
    def draw_rect(self, *args, **kwargs):
        pass

    @abstractmethod
    def draw_polygon(self, *args, **kwargs):
        pass

    @abstractmethod
    def draw_circle(self, surface, color_arg, position2d, radius, width):
        pass

    @abstractmethod
    def new_font_obj(self, font_src, font_size: int):  # src can be None!
        pass

    @abstractmethod
    def new_rect_obj(self, *args):  # probably: x, y, w, h
        pass


# Step 2: Implement the interface in a concrete class
class PygameWrapper(GameEngineSublayer):
    def __init__(self):
        import pygame as pygame_mod
        self.pygame = pygame_mod

        self.sprite = Objectifier({
            'Sprite': self.pygame.sprite.Sprite,
            'Group': self.pygame.sprite.Group,
            'spritecollide': self.pygame.sprite.spritecollide
        })
        self.event = self.pygame.event
        self.display = self.pygame.display
        self.mixer = self.pygame.mixer
        self.time = self.pygame.time
        self.Surface = self.pygame.Surface
        self.transform = self.pygame.transform
        self.image = self.pygame.image
        self.key = self.pygame.key
        self.mouse = self.pygame.mouse

        # key codes
        self.K_ESCAPE = self.pygame.K_ESCAPE
        self.K_BACKSPACE = self.pygame.K_BACKSPACE
        self.K_RETURN = self.pygame.K_RETURN
        self.K_SPACE = self.pygame.K_SPACE
        self.K_UP = self.pygame.K_UP
        self.K_LEFT = self.pygame.K_LEFT
        self.K_DOWN = self.pygame.K_DOWN
        self.K_RIGHT = self.pygame.K_RIGHT

        # pygame constants
        self.SRCALPHA = self.pygame.SRCALPHA
        self.RLEACCEL = self.pygame.RLEACCEL
        self.QUIT = self.pygame.QUIT
        self.KEYDOWN = self.pygame.KEYDOWN
        self.KEYUP = self.pygame.KEYUP
        self.MOUSEBUTTONDOWN = self.pygame.MOUSEBUTTONDOWN
        self.MOUSEBUTTONUP = self.pygame.MOUSEBUTTONUP

    def init(self):
        self.pygame.init()

    def quit(self):
        self.pygame.quit()

    def image_load(self, fileobj_or_path, *args):
        if len(args) > 0:
            return self.pygame.image.load(fileobj_or_path, namehint=args[0])
        return self.pygame.image.load(fileobj_or_path)

    def draw_circle(self, surface, color_arg, position2d, radius, width):
        self.pygame.draw.circle(surface, color_arg, position2d, radius, width)

    def fire_up_backend(self, user_id: int) -> dict:
        # Example: Fetch data from a REST API
        return {"user_id": user_id, "name": "Bob", "role": "User"}

    def draw_line(self, *args, **kwargs):
        self.pygame.draw.line(*args, **kwargs)

    def draw_rect(self, *args, **kwargs):
        self.pygame.draw.rect(*args, **kwargs)

    def draw_polygon(self, *args, **kwargs):
        self.pygame.draw.polygon(*args, **kwargs)

    def new_font_obj(self, font_src, font_size: int):  # src can be None!
        return self.pygame.font.Font(font_src, font_size)

    def new_rect_obj(self, *args):  # probably: x, y, w, h
        return self.pygame.Rect(*args)


class WebGlBackendBridge(GameEngineSublayer):
    def fire_up_backend(self, user_id: int) -> dict:
        # Example: Fetch data from MySQL
        return {"user_id": user_id, "name": "Alice", "role": "Admin"}
