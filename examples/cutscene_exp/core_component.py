

class Component:
    """
    Base class for all components
    """
    def __init__(self):
        self.key = None
        self.init()

    def init(self):
        pass

    def reset(self):
        pass
