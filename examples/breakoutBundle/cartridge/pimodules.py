

def __getattr__(name):
    global upward_link
    return upward_link[name]


upward_link = None
