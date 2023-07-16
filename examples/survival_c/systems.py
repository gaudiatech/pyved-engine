"""
systems.py

Adding all game-specific systems here!
"""
import random
import shared
import pyved_engine as pyv
from pyved_engine import *  # need to import all constants for keys etc.


__all__ = [  # Careful: the order specified below... It really matters!
    'handle_player_input',
    'update_player_state',
    'update_positions',
    'render_graphics',
]


def _blit_rot_center(surf, image, topleft, angle):
    rotated_image = surface_rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft=topleft).center)
    surf.blit(rotated_image, new_rect)


def _draw_player(scr):
    pl_obj = find_by_archetype("Player")
    ma_gfx, pos2d, g = dissect_entity(pl_obj, ["Gfx", "Position2d", "Gun"])
    angle = g["Angle"]
    player_spritesheet, player_style = ma_gfx["Spritesheet"], ma_gfx["Style"]
    _blit_rot_center(scr, player_spritesheet.image_by_rank(player_style), pos2d, angle)


# -------- SYSTEM_FUNC per se ------
def update_positions(entities, components):
    for entity in entities:
        if archetype_of(entity) == "Player":  # is player
            position = entity["Position2d"]
            speed = entity["Speed"]
            entity["Position2d"] = [position[0] + speed[0], position[1] + speed[1]]
        elif archetype_of(entity) == "Zombie":
            dx = random.randint(-1, 1)
            dy = random.randint(-1, 1)
            x, y = entity["Position2d"]
            entity["Position2d"] = (x + dx, y + dy)


def render_graphics(entities, components):
    pyv.vars.screen.fill((0, 0, 0))  # Clear screen before rendering

    for entity in entities:
        if archetype_of(entity) == "Zombie":
            x, y = entity["Position2d"]
            color = entity["Color"]
            draw_polygon(pyv.vars.screen, color, [(x, y), (x + 20, y), (x + 10, y + 20)])

        if "Gun" in entity:
            # - old way to draw the player

            # if "Position2d" in entity:
            #     x, y = entity["Position2d"]
            #     gun = entity["Gun"]
            #     angle = gun["Angle"]
            #     draw_line(gl_vars.screen, (255, 255, 0), (x + 10, y + 10),
            #               (x + 10 + 20 * math.cos(angle), y + 10 + 20 * math.sin(angle)), 2)

            # - new way to draw the player
            _draw_player(pyv.vars.screen)


def handle_player_input(entities, components):
    keys = get_pressed_keys()
    player = find_by_archetype("Player")
    if keys[K_SPACE]:
        _pressed_space = True
    else:
        if shared.space_pressed:
            _pressed_space = False
            x = player["Gfx"]["Style"]
            player["Gfx"]["Style"] = (x + 1) % shared.NB_STYLES
    if keys[K_UP]:
        player["Position2d"][1] -= 2
    elif keys[K_DOWN]:
        player["Position2d"][1] += 2

    if keys[K_LALT] or keys[K_RALT]:
        if keys[K_RIGHT]:
            player["Position2d"][0] += 2
        elif keys[K_LEFT]:
            player["Position2d"][0] -= 2
    else:
        if keys[K_RIGHT] or keys[K_LEFT]:
            if keys[K_LEFT]:
                player["Gun"]["dAngle"] = -0.1
            else:
                player["Gun"]["dAngle"] = +0.1
        else:
            player["Gun"]["dAngle"] = 0.0


def update_player_state(entities, components):
    player = find_by_archetype("Player")
    if "Gun" in player:
        if "Angle" in player["Gun"]:
            player["Gun"]["Angle"] += player["Gun"]["dAngle"]
