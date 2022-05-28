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
    DELTA8 = ((-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1))

    def __init__(self, mymap, start, goal, blocked_fun, blocked_tiles=()):
        # blocked_fun is a function that takes mymap, x, y and returns True if movement into that tile is blocked.
        self.start = start
        self.goal = goal
        self.blocked_tiles = set(blocked_tiles)
        self.mymap = mymap
        self.blocked_fun = blocked_fun
        frontier = PriorityQueue()
        frontier.put(start, 0)
        self.came_from = {}
        self.cost_to_tile = {}
        self.came_from[start] = None
        self.cost_to_tile[start] = 0

        while not frontier.empty():
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
        x, y = pos
        for dx, dy in self.DELTA8:
            x2, y2 = x + dx, y + dy
            if not ((x2, y2) in self.blocked_tiles or self.blocked_fun(mymap, x2, y2)):
                yield (x2, y2)
            elif (x2, y2) == self.goal:
                yield self.goal

    def movecost(self, a, b):
        return 1 + abs(a[0] - b[0]) + abs(a[1] - b[1])

    def heuristic(self, a, b):
        # Manhattan distance on a square grid
        return (abs(a[0] - b[0]) + abs(a[1] - b[1])) * 10
