import heapq


class AstarPathfinder:
    """
    used by isometric tech demos. For now, this implementation is dependent on the .isometric
    engine add-on, since
    the type for the 1st parameter (my_map) has to be an <pyv.isometric.model.IsometricMap> object
    """

    DELTA8 = ((-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1))
    DELTA4 = ((0, -1), (-1, 0), (1, 0), (0, 1))

    def __init__(self, iso_map_model, start, goal, blocked_fun, clamp_fun, wrap_x=False, wrap_y=False, move_diagonally=True,
                 blocked_tiles=()):
        # Preserve the original method interface and structure
        self.map = iso_map_model

        self.adhoc_delta = self.DELTA8 if move_diagonally else self.DELTA4
        self.start = clamp_fun(start)
        self.goal = clamp_fun(goal)

        self.blocked_fun = blocked_fun
        self.clamp_fun = clamp_fun
        self.wrap_x = wrap_x
        self.wrap_y = wrap_y
        self.blocked_tiles = set(blocked_tiles)

        # Our implem of priority queue uses heapq directly
        frontier = [(0, self.start)]
        self.came_from = {self.start: None}
        self.cost_to_tile = {self.start: 0}

        while frontier:
            _, current = heapq.heappop(frontier)
            if current == self.goal:
                break
            for next_cell in self.neighbors(iso_map_model, current):
                new_cost = self.cost_to_tile[current] + self.movecost(current, next_cell)
                if (next_cell not in self.cost_to_tile) or (new_cost < self.cost_to_tile[next_cell]):
                    self.cost_to_tile[next_cell] = new_cost
                    priority = new_cost + self.heuristic(self.goal, next_cell)
                    heapq.heappush(frontier, (priority, next_cell))
                    self.came_from[next_cell] = current
        self.results = self.get_path(goal)

    def get_path(self, goal):
        path = []
        current = goal
        while current is not None:
            path.append(current)
            current = self.came_from.get(current)
        path.reverse()
        return path if path[0] == self.start else []

    def neighbors(self, mymap, pos):
        # Keep original `neighbors` logic intact due to the specialized `mymap` type.
        x, y = pos
        for dx, dy in self.adhoc_delta:
            x2, y2 = self.clamp_fun((x + dx, y + dy))
            if (x2, y2) == self.goal or not ((x2, y2) in self.blocked_tiles or self.blocked_fun(mymap, x2, y2)):
                yield (x2, y2)

    def movecost(self, a, b):
        xcost = abs(a[0] - b[0]) % self.map.width if self.wrap_x else abs(a[0] - b[0])
        ycost = abs(a[1] - b[1]) % self.map.height if self.wrap_y else abs(a[1] - b[1])
        return 1 + xcost + ycost

    def heuristic(self, a, b):
        dx = abs(a[0] - b[0]) % self.map.width if self.wrap_x else abs(a[0] - b[0])
        dy = abs(a[1] - b[1]) % self.map.height if self.wrap_y else abs(a[1] - b[1])
        return dx + dy


class DijkstraPathfinder:
    @staticmethod
    def find_path(espace_matr, source_pos, dest_pos, limitations_wh=None):
        """
        :param espace_matr:
        :param source_pos:
        :param dest_pos:
        :param limitations_wh:
        :return: soit None, soit une liste de coords
        """
        chemin_inv = dict()  # on anticipe le backtrace code, en vue de retourner le plus court chemin
        candidats = set()
        src = tuple(source_pos)
        dest = tuple(dest_pos)

        # --- initialisation distance à tous les pts
        dist = dict()
        if limitations_wh:
            limit_x, limit_y = limitations_wh
        else:
            limit_x, limit_y = espace_matr.get_size()

        binf_x, bsup_x = src[0] - limit_x, src[0] + limit_x
        binf_y, bsup_y = src[1] - limit_y, src[1] + limit_y
        for x in range(binf_x, bsup_x + 1):
            for y in range(binf_y, bsup_y + 1):
                k = (x, y)
                if espace_matr.is_out(*k):
                    continue
                dist[k] = 99999
                candidats.add(k)
        dist[src] = 0

        visited = set()  # représente l'ensemble des sommets déjà visités

        while len(candidats) > 0:
            # select the element of Q with the min. distance
            # cest à dire on va explorer le sommet listé dans Q, de distance minimale
            dist_minimale = 999999
            u = None
            for sommet_a_explorer in candidats:
                if dist[sommet_a_explorer] < dist_minimale:
                    dist_minimale = dist[sommet_a_explorer]
                    u = sommet_a_explorer

            # on indique que u est exploré
            candidats.remove(u)
            visited.add(u)

            # exploration : calcul des voisins de u
            voisins = list()
            les_possib = [
                (u[0] - 1, u[1]),
                (u[0] + 1, u[1]),
                (u[0], u[1] + 1),
                (u[0], u[1] - 1),
            ]
            for k in les_possib:
                if espace_matr.is_out(*k):
                    continue
                if not (binf_x <= k[0] <= bsup_x):
                    continue
                if not (binf_y <= k[1] <= bsup_y):
                    continue
                if espace_matr.get_val(*k):
                    continue  # blocage
                voisins.append(k)

            for v in voisins:  # m-à-j plus courtes distances pr arriver à v
                w = 1
                if dist[v] > dist[u] + w:
                    dist[v] = dist[u] + w
                    chemin_inv[v] = u

        # tous les candidats ont été testés => backtrace code c-à-d reconstruction chemin le + court
        chemin = [dest]
        x = dest
        no_way = False
        while x != src:
            if x not in chemin_inv:
                no_way = True
                break
            x = chemin_inv[x]
            chemin.insert(0, x)  # insertion en 1ère position

        if no_way:
            return None
        return chemin
