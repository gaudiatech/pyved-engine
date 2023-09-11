# base class for all components
class Component:

    def __init__(self):
        self.key = None
        self.init()

    def init(self):
        pass

    def reset(self):
        pass