import pygame
import math
import os
import pickle

import pyved_engine as pyv
# from .colours import *
from renderer import Renderer
# from ..utils.utils import sortByX, sortByY, sortByZ
# from ..gamma import screen, systemManager, sceneManager, windowSize
import gamedefs
# from ..utils.utils import *
from gutils import sortByZ


# import drawRect


class Scene:

    def __init__(self,

                 # optional parameters
                 menu=None,
                 background=None,
                 backgroundAlpha=255,

                 map=None,
                 entities=None,
                 velocityForces=None,
                 accelerationForces=None

                 ):

        # key to sort
        self.orderKey = sortByZ
        self.orderWhen = 'added'  # 'always', 'added' or 'never'

        # store map
        self.map = map

        # create scene entity list
        if entities is None:
            self.entities = []
        else:
            self.entities = entities

        # create scene forces dictionary
        if velocityForces is None:
            velocityForces = {}
        if accelerationForces is None:
            accelerationForces = {}
        self.forces = {
            'velocity': velocityForces,
            'acceleration': accelerationForces
        }

        # entities to delete
        self.delete = []

        # a flag to mark entities for reordering
        self.reorderEntities = False

        self.cutscene = None
        self.frame = 0
        self.menu = menu
        self.buttons = []
        self.resetEffects()

        self.background = background
        self.backgroundAlpha = backgroundAlpha

        self.drawSceneBelow = False

        self.renderer = Renderer(self)

        self.init()

    def init(self):
        pass

    def resetEffects(self):
        self.widthPercentage = 100
        self.heightPercentage = 100
        self.leftPercentage = 0
        self.topPercentage = 0

    def setMenu(self, menu, scene):
        self.menu = menu
        self.menu.scene = scene

    def addButton(self, button):
        self.buttons.append(button)

    def _onEnter(self):
        if self.menu is not None:
            self.menu.setActiveButton()
        self.onEnter()

    def onEnter(self):
        pass

    def _onExit(self):
        if self.menu is not None:
            self.menu.reset()
        self.onExit()

    def onExit(self):
        pass

    def _update(self):

        # update frame and call scene-specific update method
        self.frame += 1
        self.update()

        # - tom - disabled cause its done elsewhere(systems.py)
        # update systems
        #for sys in systemManager.systems:
        #    sys._update(self)

        # update cutscene
        if self.cutscene is not None:
            self.cutscene.update(self)

        # update menu
        if self.menu is not None:
            self.menu.update()

        # update buttons
        for b in self.buttons:
            b.update()

        # - tom - /!\NO autoUpdate of entities! We need systems for that
        # update entities
        # for e in self.entities:
        #    e._update()

        # - tom - idem
        # update entity timed actions
        # for e in self.entities:
        #     for action in e.actions:
        #         action[0] = max(0, action[0] - 1)
        #         if action[0] == 0:
        #             action[1]()
        #             e.actions.remove(action)

        # reorder scene entities if required
        if self.orderWhen == 'always' or (self.orderWhen == 'added' and self.reorderEntities):
            self.entities.sort(key=self.orderKey)
            if self.reorderEntities:
                self.reorderEntities = False

        # delete marked entities
        for ent_obj in self.entities:
            if 'delete' in ent_obj:
                self.entities.remove(ent_obj)

    def _draw(self):
        # calculate the scene size
        w = int(gamedefs.WIDTH / 100 * self.widthPercentage)
        h = int(gamedefs.HEIGHT / 100 * self.heightPercentage)

        # create the scene surface
        self.surface = pygame.Surface((w, h), pygame.SRCALPHA)
        if self.backgroundAlpha < 255:
            self.surface.convert_alpha()

        # draw background (colour or image)
        if self.background is not None:
            if type(self.background) is pygame.Color:
                self.surface.fill(self.background)
            else:
                self.background.draw(self.surface)

        # draw scene below if requested
        if self.drawSceneBelow:
            sceneManager.getSceneBelow(self)._draw()

        # draw scene images behind
        if self.map is not None and self.map.mapImages is not None:
            for i in self.map.mapImages:
                if i.z < 1:
                    self.renderer.add(i, scene=False)

        # draw map
        if self.map is not None:
            self.map.draw(self)

        # draw systems, which send to the renderer
        # TODO can i draw in a way that is closer that what Gamma was doing? Should I?
        # for sys in systemManager.systems:
        #    sys._draw(self)

        # draw scene images in front
        if self.map is not None and self.map.mapImages is not None:
            for i in self.map.mapImages:
                if i.z >= 1:
                    self.renderer.add(i, scene=False)

        # draw everything that was sent to the render
        self.renderer.draw()
        self.renderer.flush()

        # calculate the scene position and transparency
        x = math.ceil(pygame.display.get_surface().get_size()[0] / 100 * self.leftPercentage)
        y = math.ceil(pygame.display.get_surface().get_size()[1] / 100 * self.topPercentage)

        # draw the cutscene
        if self.cutscene is not None:
            print('cutscene draw!!')
            self.cutscene.draw(self)

        # call the scene-specific draw method
        self.draw()

        # draw the menu
        if self.menu is not None:
            self.menu.draw()

        # draw buttons
        for b in self.buttons:
            b.draw(self.surface)

        # draw the scene
        pyv.get_surface().blit(self.surface, (x, y))

    def update(self):
        pass

    def draw(self):
        pass

    def addVelocityForce(self, name, force):
        self.forces['velocity'][name] = force

    def addAccelerationForce(self, name, force):
        self.forces['acceleration'][name] = force

    def removeForce(self, name):
        if name in self.forces['velocity']:
            del self.forces['velocity'][name]
        if name in self.forces['acceleration']:
            del self.forces['acceleration'][name]

    # entity methods

    def addEntity(self, entity):
        self.entities.append(entity)
        entity.onAddedToScene()
        self.reorderEntities = True

    def deleteEntity(self, entity):
        entity.onRemovedFromScene()
        self.entities.remove(entity)

    def deleteEntityByID(self, ID):
        for e in self.entities:
            if e.ID == ID:
                self.deleteEntity(e)

    def getEntitiesByTag(self, tag, *otherTags):
        entityList = []
        for e in self.entities:
            if e.getComponent('tags').has(tag, *otherTags):
                entityList.append(e)
        return entityList

    # def getEntityByID(self, entityID):
    #     for e in self.entities:
    #         if e.ID == entityID:
    #             return e
    #     return None

    def getEntitiesWithComponent(self, *componentKeys):
        # new --
        return pyv.find_by_components(*componentKeys)

    # old --
    #     entityList = []
    #     print('full list of entities:', self.entities)
    #     for e in self.entities:
    #         if e.hasComponent(*componentKeys):
    #             entityList.append(e)
    #     return entityList

    def clear(self):
        self.entities = []
        self.map = None

    # map methods

    def setMap(self, map):
        self.map = map

    def loadMap(self, filename):
        filename = os.path.abspath(filename)
        map = pickle.load(open(filename, "rb"))
        map.editorMode = False
        return map

    def saveMap(self, map, filename):
        map.editorMode = False
        filename = os.path.abspath(filename)
        pickle.dump(map, open(filename, "wb"))
