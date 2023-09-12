import pyved_engine
import shared


__all__ = [  # Careful: the order specified below... It really matters!
    'input_system',
    'update_scenes_system',
    'render_graphics',
]


def input_system(entities, componets):  # why components?
    pygame = pyved_engine.pygame
    pkeys = pygame.key.get_pressed()
    if pkeys[pygame.K_RETURN]:
        if not shared.already_pressed:
            print('cutscene launched!')
            shared.cutScene.reset()
            shared.mainScene.cutscene = shared.cutScene
            shared.already_pressed = True
    else:
        if shared.already_pressed:
            shared.already_pressed = False


def update_scenes_system(entities, components):
    shared.mainScene._update()


def render_graphics(entities, components):
    # Clear screen before rendering
    pyved_engine.vars.screen.fill((0, 77, 0))
    shared.mainScene._draw()
    # print('flip ok')
    pyved_engine.flip()
    # for entity_o in entities:
        # if pyv.archetype_of(entity_o) == "player":
            # cam = entity_o['cam']
            # x, y = entity_o['position']
            # pyv.draw_polygon(pyv.vars.screen, 'pink', [(x, y), (x + 20, y), (x + 10, y + 20)])
    # print(dir(mainScene.renderer))
