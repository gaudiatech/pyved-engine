"""
systems.py

Adding all game-specific systems here!
"""
import random
import shared
import pyved_engine as pyv


__all__ = [  # Careful: the order specified below... It really matters!
    'handle_player_input',
    'update_player_state',
    'update_positions',
    'render_graphics',
]


def _blit_rot_center(surf, image, topleft, angle):
    rotated_image = pyv.surface_rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft=topleft).center)
    surf.blit(rotated_image, new_rect)


def _draw_player(scr):
    pl_obj = pyv.find_by_archetype("Player")
    ma_gfx, pos2d, g = pyv.dissect_entity(pl_obj, ["Gfx", "Position2d", "Gun"])
    angle = g["Angle"]
    player_spritesheet, player_style = ma_gfx["Spritesheet"], ma_gfx["Style"]
    _blit_rot_center(scr, player_spritesheet.image_by_rank(player_style), pos2d, angle)


# -------- SYSTEM_FUNC per se ------
def update_positions(entities, components):
    for entity in entities:
        if pyv.archetype_of(entity) == "Player":  # is player
            position = entity["Position2d"]
            speed = entity["Speed"]
            entity["Position2d"] = [position[0] + speed[0], position[1] + speed[1]]
        elif pyv.archetype_of(entity) == "Zombie":
            dx = random.randint(-1, 1)
            dy = random.randint(-1, 1)
            x, y = entity["Position2d"]
            entity["Position2d"] = (x + dx, y + dy)


def render_graphics(entities, components):
    pyv.vars.screen.fill((0, 0, 0))  # Clear screen before rendering

    for entity in entities:
        if pyv.archetype_of(entity) == "Zombie":
            x, y = entity["Position2d"]
            color = entity["Color"]
            pyv.draw_polygon(pyv.vars.screen, color, [(x, y), (x + 20, y), (x + 10, y + 20)])

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
    global _pressed_space
    keys = pyv.get_pressed_keys()
    player = pyv.find_by_archetype("Player")
    if keys[pyv.pygame.K_SPACE]:
        shared.space_pressed = True
    else:
        if shared.space_pressed:
            shared.space_pressed = False
            x = player["Gfx"]["Style"]
            player["Gfx"]["Style"] = (x + 1) % shared.NB_STYLES
            # print('style changes -> trigger')

    if keys[pyv.pygame.K_UP]:
        player["Position2d"][1] -= 2
    elif keys[pyv.pygame.K_DOWN]:
        player["Position2d"][1] += 2

    if keys[pyv.pygame.K_LALT] or keys[pyv.pygame.K_RALT]:
        if keys[pyv.pygame.K_RIGHT]:
            player["Position2d"][0] += 2
        elif keys[pyv.pygame.K_LEFT]:
            player["Position2d"][0] -= 2
    else:
        if keys[pyv.pygame.K_RIGHT] or keys[pyv.pygame.K_LEFT]:
            if keys[pyv.pygame.K_LEFT]:
                player["Gun"]["dAngle"] = -0.1
            else:
                player["Gun"]["dAngle"] = +0.1
        else:
            player["Gun"]["dAngle"] = 0.0


def update_player_state(entities, components):
    player = pyv.find_by_archetype("Player")
    if "Gun" in player:
        if "Angle" in player["Gun"]:
            player["Gun"]["Angle"] += player["Gun"]["dAngle"]
