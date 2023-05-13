# Cribbed from the Red Blob Games tutorial.
import heapq


class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]


class AStarPath(object):
    DELTA8 = (
        (-1, -1),
        (0, -1),
        (1, -1),

        (-1, 0),
        (1, 0),

        (-1, 1),
        (0, 1),
        (1, 1))
    # DELTA4 = ((0, -1), (-1, 0), (1, 0), (0, 1))

    def __init__(self, mymap, start, goal, blocked_fun, clamp_fun, wrap_x=False, wrap_y=False, blocked_tiles=()):
        # blocked_fun is a function that takes mymap, x, y and returns True if movement into that tile is blocked.y
        # clamp_fun is a function that takes (x,y) and clamps the values if needed.

        # TEMP disabled clamp bc it creates BUGS! in niobe

        # start = clamp_fun(start)
        self.start = start
        # goal = clamp_fun(goal)
        self.goal = goal
        self.blocked_tiles = set(blocked_tiles)
        self.mymap = mymap
        self.blocked_fun = blocked_fun
        self.clamp_fun = lambda x:x  # clamp_fun
        self.wrap_x = wrap_x
        self.wrap_y = wrap_y
        frontier = PriorityQueue()
        frontier.put(self.start, 0)
        self.came_from = {}
        self.cost_to_tile = {}
        self.came_from[self.start] = None
        self.cost_to_tile[self.start] = 0
        self.cpt = 0
        while not frontier.empty() and self.cpt < 256:
            current = frontier.get()
            if current == goal:
                break
            for next in self.neighbors(mymap, current):
                new_cost = self.cost_to_tile[current] + self.movecost(current, next)
                if next not in self.cost_to_tile or new_cost < self.cost_to_tile[next]:
                    self.cost_to_tile[next] = new_cost
                    priority = new_cost + self.heuristic(goal, next)
                    frontier.put(next, priority)
                    self.came_from[next] = current
        self.results = self.get_path(goal)

    def get_path(self, goal):
        results = list()
        p = goal
        while p:
            results.append(p)
            p = self.came_from.get(p)
        results.reverse()
        if results[0] != self.start:
            results = list()
        return results

    def neighbors(self, mymap, pos):
        self.cpt += 1
        x, y = pos
        for dx, dy in self.DELTA8:
            #x2, y2 = x + dx, y + dy
            x2, y2 = self.clamp_fun((x + dx/2, y + dy/2))
            #x2, y2 = int(x2), int(y2)
            if not( ((x2, y2) in self.blocked_tiles) or self.blocked_fun(mymap, int(x2), int(y2)) ):
                yield (x2, y2)
            elif (x2, y2) == self.goal:
                yield self.goal

    def movecost(self, a, b):
        xcost = abs(a[0] - b[0])
        ycost = abs(a[1] - b[1])
        if self.wrap_x:
            xcost = min(xcost, self.mymap.width - xcost)
        if self.wrap_y:
            ycost = min(ycost, self.mymap.height - ycost)
        return 1 + xcost + ycost

    def heuristic(self, a, b):
        # Manhattan distance on a square grid
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        if self.wrap_x:
            dx = min(dx, self.mymap.width - dx)
        if self.wrap_y:
            dy = min(dy, self.mymap.height - dy)
        return dx + dy
