from math import ceil
import gamedefs
# from ..gamma import windowSize
# from ..utils.utils import drawRect
# from .colours import *
from rectangle import Rectangle


class Cutscene:

    def __init__(self):
        # list of actions to perform
        self.actionList = []
        # current action to perform
        self.actionIndex = 0

        self.fadePercentage = 0
        self.inOutDuration = 60
        self.lettboxColour = "black"  # BLACK
        self.lettboxHeight = 30
        
        # status is either:
        # in = fading in
        # do = performing the scene
        # out = fading out
        self.status = 'in'

        self.currentDelay = 0

    def setDelay(self, amount):
        self.currentDelay = amount

    def advance(self):
        self.actionIndex += 1

    def reset(self):
        self.actionIndex = 0
        self.fadePercentage = 0
        self.status = 'in'

    def update(self, scene):
        # fading in
        if self.status == 'in':
            self.fadePercentage = min(100, self.fadePercentage+(100/self.inOutDuration))
            if self.fadePercentage == 100:
                self.status = 'do'

        # fading out
        if self.status == 'out':
            self.fadePercentage = max(0, self.fadePercentage-(100/self.inOutDuration))
            if self.fadePercentage == 0:
                scene.cutScene = None

        # performing cutscene
        if self.status == 'do':

            if len(self.actionList) > self.actionIndex:
                if self.currentDelay == 0:
                    self.actionList[self.actionIndex]()
                if self.currentDelay == 0:
                    self.advance()
                
                if self.currentDelay > 0:
                    self.currentDelay -= 1
                    if self.currentDelay == 0:
                        self.advance()

            else:
                self.status = 'out'
                
    def draw(self, scene):
        # top letterbox
        Rectangle(
            0, 0,
            gamedefs.WIDTH, ceil(self.lettboxHeight * (self.fadePercentage / 100)),
            colour=self.lettboxColour
        ).draw(scene.surface)

        # bottom letterbox
        Rectangle(
            0, ceil(gamedefs.HEIGHT - (self.lettboxHeight * (self.fadePercentage / 100))),
            gamedefs.WIDTH, self.lettboxHeight * (self.fadePercentage / 100),
            colour=self.lettboxColour
        ).draw(scene.surface)
