

upward_link = None


def __getattr__(name):
    global upward_link
    # debug
    # print('pimodules is tryin to provide...', name)
    return upward_link[name]
