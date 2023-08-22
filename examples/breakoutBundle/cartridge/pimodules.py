

upward_link = None


def __getattr__(name):
    global upward_link
    print('pimodules tryin to provide...', name)
    return upward_link[name]
