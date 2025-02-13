
from abc import ABC, abstractmethod


# Step 1: Define an interface (abstract class)
class GameEngineSublayer(ABC):
    """
    this is used solely to specify the full interface of the Gamedev API
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
