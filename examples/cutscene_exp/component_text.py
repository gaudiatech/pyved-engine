#from .gamma import soundManager, inputManager
#from .core.component import Component
#from .core.colours import *
#from ..renderables.text import Text
from core_component import Component
import pygame

# used to be the import.set of file embedding cls:Text
# from ..gamma import resourceManager
# from ..core.renderable import Renderable
# from ..core.colours import WHITE
# from ..utils.utils_draw import blit_alpha


class Text:

    def __init__(self,
                 # required parameters
                 text, x, y,
                 # optional parameters
                 hAlign='left', vAlign='top',
                 colour="white",
                 alpha=255,
                 font=None,  #resourceManager.getFont('munro24'),
                 underline=False,
                 z=1,
                 xParallax=False, yParallax=False

                 ):
        super().__init__(x, y, z, hAlign, vAlign, colour, alpha, xParallax, yParallax)
        if font is None:
            self.font = pygame.font.Font(None, 15)
        else:
            self.font = font

        # set additional text object parameters
        self._text = str(text)

        self.underline = underline
        self._createSurface()

    def _createSurface(self):
        self.font.set_underline(self.underline)
        self.textSurface = self.font.render(self._text, True, self.colour)
        self.rect = self.textSurface.get_rect()
        self._align()

    def draw(self, surface, xOff=0, yOff=0, scale=1):
        x = self.rect.x * scale + xOff
        y = self.rect.y * scale + yOff
        blit_alpha(surface, self.textSurface, (x, y), self._alpha)

        #  text property

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = str(value)
        self._createSurface()


class TextComponent(Component):

    def __init__(self,
    
        # required parameters

        text,
        
        # optional parameters
        
        # position (only if overhead = False)
        x = 20, y = 20,
        # colour
        textColour = "white",
        # minimum text character width
        textWidth = 20,
        # spacing between rows of text
        spacing = 15,
        # display above the entity, or at bottom of scene
        overhead = True,
        # how long to display the text
        # options are 'always', 'timed', or 'press'
        lifetime = 'always',
        # how the text appears
        # options are 'appear', 'fade' or 'tick'
        type = 'appear',
        # display a new character every [x] frames
        tick_delay = 5,
        # sound to play when advancing tick animation
        tick_sound = None,
        # display time before fading out (if lifetime='fade')
        final_display_time = 300,
        # inputs that can control the text (if lifetime='press')
        input_list = None
        
    ):

        self.key = 'text'

        # store component attributes
        
        self.text = text
        self.x = x
        self.y = y
        self.textColour = textColour
        self.textWidth = textWidth
        self.spacing = spacing
        self.overhead = overhead
        self.lifetime = lifetime
        self.tick_delay = tick_delay
        self.tick_sound = tick_sound
        self.final_display_time = final_display_time
        self.input_list = input_list
        self._setType(type)

        # attributes to store current state

        # timer used to tick the text forward
        self.delayTimer = self.tick_delay
        # stores the text, divided into rows
        self.textList = []
        # lets the TextSystem know when to delete the component
        self.destroy = False
        # keeps track of fade direction (in or out)
        self.enterOrExit = 'enter'

        # split the text into multiple rows,
        # using self.width as a minimum characher width

        row = ''
        for char in self.text:
            row = row + char
            if len(row) >= self.textWidth and char == ' ':
                self.textList.append(row[:-1])
                row = ''
        if len(row) > 0:
            self.textList.append(row)
        
        # add hint to press button
        if self.lifetime == 'press':
            self.textList[-1] += '  >>'

    def _setType(self, type):

        # types are 'appear', 'tick' or 'fade'
        self.type = type
        
        if self.type == 'appear':
            self.finished = True
            self.index = self.width
            self.row = len(self.textList)
            self.fadeAmount = 255
        
        if self.type == 'tick':
            self.finished = False
            self.index = 0
            self.row = 0
            self.fadeAmount = 255
        
        if self.type == 'fade':
            self.fadeAmount = 0
            self.finished = False
            self.index = self.width
            self.row = len(self.textList)

    def update(self):

        # no need to update if just showing all text
        if self.type == 'appear':
            pass

        # if text is appearing ticked
        if self.type == 'tick' and self.enterOrExit == 'enter':
            if not self.finished:
                # wait for tick timer
                self.delayTimer -= 1
                if self.delayTimer <= 0:
                    self.delayTimer = self.tick_delay
                    # increment text
                    self.index += 1
                    if self.tick_sound:
                        soundManager.playSound(self.tick_sound, soundManager.soundVolume / 2)
                    # move to tick the next row of text
                    if self.index >= len(self.textList[self.row]):
                        self.index = 0
                        self.row += 1
                        # finish once at the end of the last row
                        if self.row >= len(self.textList):
                            self.finished = True

        # if fading in
        if self.type == 'fade' and self.enterOrExit == 'enter':
            self.fadeAmount = min(self.fadeAmount+4, 255)
            if self.fadeAmount == 255:
                self.finished = True

        # start exising once enter animations complete
        if self.finished and self.enterOrExit == 'enter':

            if self.lifetime == 'always':
                pass

            if self.lifetime == 'timed':
                self.final_display_time -= 1
                if self.final_display_time <= 0:
                    self.enterOrExit = 'exit'

        # press to advance, regardless of progress
        if self.lifetime == 'press':
            if self.input_list is not None:
                for input in self.input_list:
                    if inputManager.isPressed(input):
                        self.enterOrExit = 'exit'

        # fade out the required amount (may be none)
        # and then destroy component
        if self.enterOrExit == 'exit':

            self.fadeAmount = max(self.fadeAmount - 5, 0)
            if self.fadeAmount == 0:
                self.destroy = True

    def draw(self, scene, x, y):      

        rows = self.spacing * len(self.textList)

        for i,l in enumerate(self.textList):

            # don't draw all of the current row if ticking
            if i == self.row:

                if self.overhead:

                    # draw above the entity
                    scene.renderer.add(Text(
                        l[0:self.index],
                        x,
                        y-10-rows+(i*self.spacing),
                        colour=self.textColour,
                        alpha=self.fadeAmount
                    ), scene=False)

                else:

                    # draw at required x/y position
                    scene.renderer.add(Text(
                        l[0:self.index],
                        self.x,
                        self.y+(i*self.spacing*2),
                        colour=self.textColour,
                        alpha=self.fadeAmount
                    ))   

            # draw previous rows
            elif i < self.row:

                if self.overhead:

                    # draw above the entity
                    scene.renderer.add(Text(
                        l,
                        x,
                        y-10-rows+(i*self.spacing),
                        colour=self.textColour,
                        alpha=self.fadeAmount
                    ), scene=False)
                
                else:
                    
                    # draw at required x/y position
                    scene.renderer.add(Text(
                        l,
                        self.x,
                        self.y+(i*self.spacing*2),
                        colour=self.textColour,
                        alpha=self.fadeAmount
                    ))
