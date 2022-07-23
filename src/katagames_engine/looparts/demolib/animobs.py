from ... import _hub

pygame = _hub.pygame  # alias to keep on using pygame, easily

import math


def get_line(x1, y1, x2, y2):
    # Bresenham's line drawing algorithm, as obtained from RogueBasin.
    points = []
    issteep = abs(y2 - y1) > abs(x2 - x1)
    if issteep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
    rev = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        rev = True
    deltax = x2 - x1
    deltay = abs(y2 - y1)
    error = int(deltax / 2)
    y = y1
    ystep = None
    if y1 < y2:
        ystep = 1
    else:
        ystep = -1
    for x in range(x1, x2 + 1):
        if issteep:
            points.append((y, x))
        else:
            points.append((x, y))
        error -= deltay
        if error < 0:
            y += ystep
            error += deltax
    # Reverse the list if the coordinates were reversed
    if rev:
        points.reverse()
    return points


def get_fline(p1, p2, speed):
    # Generate a line, but of floats, ending with the ints x2,y2.
    points = list()
    rng = math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
    steps = int(rng / speed)
    fsteps = float(rng / speed)
    for t in range(0, steps):
        newpoint = list()
        for coord in range(len(p1)):
            newpoint.append(p1[coord] + float((p2[coord] - p1[coord]) * t) / fsteps)
        points.append(newpoint)
    points.append(p2)
    return points


class MoveModel(object):
    def __init__(self, model, dest, speed=0.1, delay=0):
        self.model = model
        self.speed = speed
        self.dest = dest
        self.delay = delay
        self.step = 0
        self.needs_deletion = False
        self.children = list()
        start = (model.x, model.y)
        self.itinerary = get_fline(start, dest, speed)

    def update(self):
        # This one doesn't appear directly, but moves a model.
        if self.delay > 0:
            self.delay += -1
        elif self.itinerary:
            self.model.x, self.model.y = self.itinerary.pop(0)
            if not self.itinerary:
                self.needs_deletion = True
        else:
            self.needs_deletion = True


class WatchMeWiggle(object):
    # Bear with me. When a model attacks, sometimes it's not clear which model is attacking. So,
    # what I'm gonna do is wiggle the model doing the action, so you can see who it is.
    # Tried to think of a clever name but "WatchMeWiggle" was the best I came up with. You see, the model
    # wiggles, because that's the model you're supposed to be watching right now.
    def __init__(self, model, delay=0, duration=5):
        self.model = model
        self.duration = duration
        self.delay = delay
        self.step = 0
        self.needs_deletion = False
        self.children = list()

    WIGGLE_POS = ((0, 1), (0, 2), (0, 1), (0, 0), (0, -1), (0, -2), (0, -1), (0, 0))

    def update(self, view):
        # This one doesn't appear directly, but moves a model.
        if self.delay > 0:
            self.delay += -1
        elif self.duration > self.step:
            self.step += 1
            self.model.offset_pos = self.WIGGLE_POS[self.step % len(self.WIGGLE_POS)]
        else:
            self.model.offset_pos = None
            self.needs_deletion = True


class BlastOffAnim(object):
    # The model will fly up, up, up for around 1000 pixels. It does not come down again so if you want that you better
    # do it manually.
    def __init__(self, model, delay=0, duration=50, speed=-1, acceleration=-1):
        self.model = model
        self.duration = duration
        self.height = 0
        self.speed = speed
        self.acceleration = acceleration
        self.delay = delay
        self.step = 0
        self.needs_deletion = False
        self.children = list()

    def update(self, view):
        # This one doesn't appear directly, but moves a model.
        if self.delay > 0:
            self.delay += -1
        elif self.duration > self.step:
            self.step += 1
            self.height += self.speed
            self.speed += self.acceleration
            self.model.offset_pos = (0, self.height)
        else:
            self.needs_deletion = True
