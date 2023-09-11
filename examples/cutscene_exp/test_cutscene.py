import pygame
import os
import pyved_engine as pyv
from scene import Scene

pyv.bootstrap_e()

from component_text import TextComponent
from component_camera import CameraComponent
from cutscene import Cutscene
from manager_scene import SceneManager


mainScene = cutscene = None
already_pressed = False


def input_system(entities, componets):  # why components?
    global cutscene, mainScene, already_pressed
    pkeys = pygame.key.get_pressed()
    if pkeys[pygame.K_RETURN]:
        if not already_pressed:
            print('cutscene launched!')
            cutscene.reset()
            mainScene.cutscene = cutscene
            already_pressed = True
    else:
        if already_pressed:
            already_pressed = False
    # print('entities are', entities)


def update_scenes_system(entities, components):
    global mainScene
    mainScene._update()


def render_graphics(entities, components):
    global mainScene
    # Clear screen before rendering
    pyv.vars.screen.fill((0, 77, 0))
    mainScene._draw()
    # print('flip ok')
    pyv.flip()

    # for entity_o in entities:
        # if pyv.archetype_of(entity_o) == "player":
            # cam = entity_o['cam']
            # x, y = entity_o['position']
            # pyv.draw_polygon(pyv.vars.screen, 'pink', [(x, y), (x + 20, y), (x + 10, y + 20)])
    # print(dir(mainScene.renderer))


@pyv.declare_begin
def test_initialize(vmst=None):
    global mainScene, cutscene
    pyv.init()

    #pyv.define_archetype("Zombie", ["Position2d", "Health", "Color"])
    #pyv.define_archetype("Player", ["Position2d", "Speed", "Gun", "Gfx"])
    sceneManager = SceneManager()
    #
    # create a main scene
    #

    mainScene = Scene()

    #
    # add some resources
    #
    # gamma.resourceManager.addTexture('player_idle_1', os.path.join('images', 'player', 'vita_00.png'))
    # gamma.resourceManager.addTexture('player_idle_2', os.path.join('images', 'player', 'vita_01.png'))
    # gamma.resourceManager.addTexture('player_idle_3', os.path.join('images', 'player', 'vita_02.png'))
    # gamma.resourceManager.addTexture('player_idle_4', os.path.join('images', 'player', 'vita_03.png'))

    #
    # create an animated player
    #
    # playerAnimation = gamma.Sprite(
    #     gamma.resourceManager.getTexture('player_idle_1'),
    #     gamma.resourceManager.getTexture('player_idle_2'),
    #     gamma.resourceManager.getTexture('player_idle_3'),
    #     gamma.resourceManager.getTexture('player_idle_4')
    # )

    # In pyv we’ve got only:
    #    gfx.SpriteSheet , gfx.JsonBasedSprSheet , and pyv.anim.AnimatedSprite
    #    therefore its hard to adapt from gamma.Sprite that uses separate images
    player_anim = pygame.sprite.Sprite()
    player_anim.image = pygame.image.load('vita_00.png')

    # TODO somehow need to bind entities to the main Scene
    # mainScene.addEntity()

    # pyv.gfx.Spritesheet(
    #    None
    # )

    # - old
    # playerEntity = gamma.Entity(
    #    gamma.PositionComponent(300, 100, 45, 51),
    #    gamma.SpritesComponent('default', playerAnimation)
    # )

    # - new
    pyv.define_archetype("player", ["position", "camera"])
    player_entity = pyv.new_from_archetype("player")
    pyv.init_entity(
        player_entity,
        {"position": [300, 100],
         "camera": CameraComponent(
             0, 0, 600, 400,
             bgColour="blue",  # gamma.BLUE,
             entityToTrack=player_entity
         )}
    )

    # -old
    # add a camera to the player
    # playerEntity.addComponent(CameraComponent(
    #     0, 0, 600, 400,
    #     bgColour = "blue",  # gamma.BLUE,
    #     entityToTrack = playerEntity
    # ))

    cutscene = Cutscene()
    cutscene.actionList = [
        lambda: player_entity['camera'].setZoom(3, duration=60),
        lambda: mainScene.cutscene.setDelay(120),

        # add component below:
        lambda: player_entity.update({'text':TextComponent('Hello! How are you?', lifetime='timed', type='tick', final_display_time=120)}),

        lambda: mainScene.cutscene.setDelay(300),
        lambda: player_entity['camera'].setZoom(1, duration=60),
        lambda: mainScene.cutscene.setDelay(60)
    ]

    # player controls = enter to start cutscene
    # def playerControls(player):
    #     if gamma.inputManager.isPressed(player.getComponent('input').b1):
    #         # start the cutscene
    #         cutscene.reset()
    #         mainScene.cutscene = cutscene

    # TODO handle the input somehow
    # playerEntity.addComponent(
    #    gamma.InputComponent(b1=gamma.keys.enter, inputContext=playerControls)
    # )

    #
    # add entities to scene
    #
    mainScene.entities.append(player_entity)
    #
    # add scene to the gamma and start
    #

    sceneManager.push(mainScene)
    for syst in (input_system, update_scenes_system, render_graphics):
        pyv.add_system(syst)


@pyv.declare_update
def test_update_func(into_t):
    for event in pyv.fetch_events():
        if event.type == pyv.pygame.QUIT:
            pyv.vars.gameover = True
    pyv.systems_proc()  # run everything described in systems


@pyv.declare_end
def test_gameover(vmst=None):
    pyv.close_game()


pyv.run_game()
