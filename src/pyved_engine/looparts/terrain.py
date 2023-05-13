

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
