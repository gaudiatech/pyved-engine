import pygame


class Renderer:

    def __init__(self, scene):

        # list of items to render
        self.worldRenderable = []
        self.sceneRenderable = []
        # a renderer is attached to a scene
        self.scene = scene
    
    # adds a renderable object to the renderer
    def add(self, r, scene=True):
        if not scene:
            self.worldRenderable.append(r)
        else:
            self.sceneRenderable.append(r)

    # removes all renderable objects from the renderer
    def flush(self):
        self.worldRenderable = []
        self.sceneRenderable = []

    def draw(self):

        #
        # WORLD RENDERING
        # draw all renderable objects, for all cameras
        #

        # iterate over all cameras
        entitiesWithCamera = self.scene.getEntitiesWithComponent('camera')
        if len(entitiesWithCamera) != 1:
            print(entitiesWithCamera)
            raise ValueError('unexpected effect')

        for e in entitiesWithCamera:

            # get the camera component
            camera = e['camera']

            # set clipping rectangle
            cameraRect = camera.rect
            clipRect = pygame.Rect(cameraRect.x, cameraRect.y, cameraRect.w, cameraRect.h)
            self.scene.surface.set_clip(clipRect)

            # fill camera background
            if camera.bgColour is not None:
                self.scene.surface.fill(camera.bgColour)

            # draw each renderable, transformed for the camera
            for r in self.worldRenderable:
                r.draw(self.scene.surface, camera._x, camera._y, camera._z)
            
            # unset clipping rectangle
            self.scene.surface.set_clip(None)
        
        #
        # SCENE RENDERING
        #

        for r in self.sceneRenderable:
            r.draw(self.scene.surface)
