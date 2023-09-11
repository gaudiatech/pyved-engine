class SceneManager:
    
    def __init__(self):
        self.storedScenes = {}
        self.scenes = []
        self.transition = None

    def storeScene(self, tag, scene):
        self.storedScenes[tag] = scene
    
    def getStoredScene(self, tag):
        return self.storedScenes[tag]

    def isEmpty(self):
        return len(self.scenes) == 0

    def enterScene(self):
        if len(self.scenes) > 0:
            self.getTopScene()._onEnter()

    def exitScene(self):
        if len(self.scenes) > 0:
            self.getTopScene()._onExit()

    def update(self):
        if self.transition is not None:
            self.transition._update()
        else:
            if len(self.scenes) > 0:
                self.getTopScene()._update()
    
    def draw(self):
        if self.transition is not None:
            self.transition._draw()
        else:
            if len(self.scenes) > 0:
                self.getTopScene()._draw()
    
    def push(self, scene):
        if not scene.drawSceneBelow:
            self.exitScene()
        self.scenes.append(scene)
        self.enterScene()

    def pop(self, scenesToPop=1):
        for i in range(scenesToPop):
            scene = self.getTopScene()
            self.exitScene()
            self.scenes.pop()
            if not scene.drawSceneBelow:
                self.enterScene()

    def set(self, scenes):
        # pop all scenes
        while len(self.scenes) > 0:
            self.pop()
        # add new scenes
        for s in scenes:
            self.scenes.append(s)   # push(s)?
        # enter the top scene
        self.enterScene()

    def clear(self):
        while len(self.scenes) > 0:
            self.pop() 

    def setTransition(self, t):
        self.transition = t

    def getTopScene(self):
        if len(self.scenes) == 0:
            return None
        return self.scenes[-1]

    def getSceneBelow(self, scene):
        if scene not in self.scenes:
            return self.getTopScene()
        if len(self.scenes) <= 1:
            return None
        return self.scenes[self.scenes.index(scene)-1]