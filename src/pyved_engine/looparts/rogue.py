import math
import random

from .. import custom_struct as struct


# ----------------------------
#  random map generation tool
# ----------------------------
SYM_UP, SYM_DOWN, SYM_LEFT, SYM_RIGHT = range(4)

DIRS = [
    SYM_UP,
    SYM_DOWN,
    SYM_LEFT,
    SYM_RIGHT]

COORD_OFFSET = {
    SYM_UP: [0, -1],
    SYM_DOWN: [0, +1],
    SYM_LEFT: [-1, 0],
    SYM_RIGHT: [+1, 0]}

WINDING_FACTOR = 0.4
SEUIL_CASES = 44


def dist_manhattan(c1, c2):
    return abs(c2[0] - c1[0]) + abs(c2[1] - c1[1])


def cell_in_range(cell, size):
    if cell[0] < 0 or cell[0] >= size[0]:
        return False
    if cell[1] < 0 or cell[1] >= size[1]:
        return False
    return True


def cell_voisinnes(c, size):
    i, j = c
    res = list()
    for d in DIRS:
        voisin_direct = (i + COORD_OFFSET[d][0], j + COORD_OFFSET[d][1])
        if cell_in_range(voisin_direct, size):
            res.append(voisin_direct)
    return res


class RandomMaze:
    """
    le but de cette classe est de générer un labyrinthe aléatoire :
    représenté via une matrice 2d à valeurs abritraires (soit None soit Nombre entier)
    représentant salles et couloirs

    Elle permet de récupérer une matrice (objet type IntegerMatrix) constante et adéquate
    pour le but recherché (disposer dun labyrinthe différent à chaque fois)
    via la méthode RandomMaze.getMatrix
    """
    def __init__(self, w, h, min_room_size, max_room_size, density_factor=140):
        self.int_matrix = struct.IntegerMatrix((w, h))
        self.int_matrix.set_all(None)  # super important! Otherwise the algorithm wont work
        self.blocking_map = struct.BoolMatrix((w, h))
        self.blocking_map.set_all(True)  # by default, all is blocking

        self.room_possib_size = list()

        for i in range(min_room_size, max_room_size + 1):
            if i % 2 == 0:  # choix dune taille impaire nécessairement
                continue
            self.room_possib_size.append(i)

        # --- pr stocker meta données
        self.curr_region = 0
        self.li_rooms = list()

        # --- procédure de constr dun labyrinthe randomize

        # (1) creation non overlaping rooms
        self.nb_rooms = 0
        self.all_room_codes = set()
        for i in range(density_factor):
            self.__add_room()

        # (2) growing tree algo
        for i in range(1, w - 1, 2):
            for j in range(1, h - 1, 2):
                pos = (i, j)
                if self.int_matrix.get_val(*pos) is None:
                    self.__growMaze(pos)

        # (3) connexion de regions (creuse les jonctions)
        self.candidats_connexion = list()
        self.li_connecteurs = list()
        dim = self.int_matrix.get_size()
        for i in range(dim[0]):
            for j in range(dim[1]):
                if self.__canBeConnector((i, j)):
                    self.candidats_connexion.append((i, j))

        self.regions_to_blobs = dict()
        while self.canMerge():
            self.stepMerge()

        # (4) suppr. cul-de-sac
        self.tested_pos = set()
        self.recUncarve((1, 1))

        # --- post-processing step: sync the data in self.blocking_map
        for i in range(dim[0]):
            for j in range(dim[1]):
                if self.int_matrix.get_val(i, j):
                    self.blocking_map.set_val(i, j, False)

    def pick_walkable_cell(self):
        # helps choosing a valid initial position for the avatar
        floor = self.int_matrix
        w, h = floor.get_size()
        chosen_pos = [
            random.randint(0, w-1),
            random.randint(0, h-1)
        ]
        while floor.get_val(*chosen_pos) is None:  # i.e. a wall
            # try again
            chosen_pos[0] = random.randint(0, w-1)
            chosen_pos[1] = random.randint(0, h-1)
        return chosen_pos
    
    def isRoomRegion(self, pos):
        val = self.int_matrix.get_val(*pos)
        return val in self.all_room_codes

    def recUncarve(self, pos):
        if pos in self.tested_pos:
            return
        self.tested_pos.add(pos)

        m_size = self.int_matrix.get_size()
        voisins = cell_voisinnes(pos, m_size)
        nb_cell_carved_v = 0  # sera un nb entre 1 et 4
        for v in voisins:
            if self.int_matrix.get_val(*v) is not None:
                nb_cell_carved_v += 1

        if nb_cell_carved_v == 1:
            self.int_matrix.set_val(pos[0], pos[1], None)
            for v in voisins:
                if v in self.tested_pos:
                    self.tested_pos.remove(v)

        for v in voisins:
            if self.int_matrix.get_val(*v) is not None:
                self.recUncarve(v)

    def __detRegionsProches(self, c):
        # -- traitement basique : lister les codes distincts des régions voisines
        m_size = self.int_matrix.get_size()
        voisins = cell_voisinnes(c, m_size)
        ens_tmp = set()
        for v in voisins:
            tmp_val = self.int_matrix.get_val(*v)
            if tmp_val is not None:
                ens_tmp.add(tmp_val)
        return list(ens_tmp)

    def __canBeConnector(self, pos):
        # un connecteur : est avant tt un mur, il doit letre
        tmp_val = self.int_matrix.get_val(*pos)
        if tmp_val is not None:
            return False

        # un connecteur : est proche de 2 régions distinctes
        codes_reg_prox = self.__detRegionsProches(pos)
        return len(codes_reg_prox) >= 2

    def __isCloseToRegion(self, pos, code):
        codes_reg_prox = self.__detRegionsProches(pos)
        return code in codes_reg_prox

    def canMerge(self):
        return len(self.candidats_connexion) > 0

    def stepMerge(self):
        COEFF_REDONDANCE = 0.3

        connect_valid = random.choice(self.candidats_connexion)
        tmp = self.__detRegionsProches(connect_valid)

        if tmp[0] in self.all_room_codes:  # on privilegie un connecteur = region de couloir
            args = [tmp[1], tmp[0]]
        else:
            args = tmp

        self.__mergeRegions(connect_valid, args[0], args[1])

        # --- On garde que les connecteurs utiles et pas trop près dun connecteur validé
        liste_filtree = list()

        for c in self.candidats_connexion:
            # -- élimination des connecteurs trop proches du nouveau connect_valid
            if dist_manhattan(c, connect_valid) <= 1:
                continue

            # -- utile pr merger?
            merging_utility = False
            cod_rp = self.__detRegionsProches(c)
            if (cod_rp[0] not in self.regions_to_blobs) or (cod_rp[1] not in self.regions_to_blobs):
                merging_utility = True
            elif self.regions_to_blobs[cod_rp[0]] != self.regions_to_blobs[cod_rp[1]]:
                merging_utility = True

            if merging_utility:
                liste_filtree.append(c)
                continue
            # -- conservation "chanceuse" de candidats inutiles
            if random.random() < COEFF_REDONDANCE:
                liste_filtree.append(c)

        self.candidats_connexion = liste_filtree

    def __findCloseWalls(self, i, j):
        murs_voisins = list()
        for d in DIRS:
            tmp = (i + COORD_OFFSET[d][0], j + COORD_OFFSET[d][1])
            if self.int_matrix.get_val(*tmp) is None:
                murs_voisins.append(tmp)
        return murs_voisins

    def __mergeRegions(self, current_cell, cod_region_a, cod_region_b):
        self.int_matrix.set_val(current_cell[0], current_cell[1], cod_region_a)

        self.candidats_connexion.remove(current_cell)
        self.li_connecteurs.append(current_cell)

        candidats_blob = list()
        if cod_region_a in self.regions_to_blobs:
            candidats_blob.append(self.regions_to_blobs[cod_region_a])
        if cod_region_b in self.regions_to_blobs:
            candidats_blob.append(self.regions_to_blobs[cod_region_b])

        if len(candidats_blob) == 0:
            # nouveau blob
            tmp_blob_codes = list(self.regions_to_blobs.values())
            if len(tmp_blob_codes) == 0:
                blob_corresp = 1
            else:
                blob_corresp = max(tmp_blob_codes) + 1
        else:
            # blob existant, on garde le num le plus petit
            blob_corresp = min(candidats_blob)

        self.regions_to_blobs[cod_region_a] = blob_corresp
        self.regions_to_blobs[cod_region_b] = blob_corresp

    def getMatrix(self):
        return self.int_matrix

    def __startRegion(self):
        self.curr_region += 1

    def getRegion(self):
        return self.curr_region

    def __add_room(self):
        taille_room = random.choice(self.room_possib_size)
        w, h = self.int_matrix.get_size()

        bsupw = w - taille_room
        bsuph = h - taille_room

        intervalle_x = [2 * x + 1 for x in range(0, bsupw // 2)]
        intervalle_y = [2 * y + 1 for y in range(0, bsuph // 2)]
        intervalle_x.pop()
        intervalle_y.pop()

        pos_salle = (
            random.choice(intervalle_x),
            random.choice(intervalle_y)
        )

        # salle empiete sur qq chose ?
        for i in range(pos_salle[0] - 1, pos_salle[0] + taille_room + 2):
            for j in range(pos_salle[1] - 1, pos_salle[1] + taille_room + 2):
                if self.int_matrix.get_val(i, j) is not None:
                    return

        # --- création room
        self.__startRegion()
        code = self.getRegion()
        self.li_rooms.append((pos_salle, taille_room, code))

        for i in range(pos_salle[0], pos_salle[0] + taille_room):
            for j in range(pos_salle[1], pos_salle[1] + taille_room):
                self.int_matrix.set_val(i, j, code)
        self.nb_rooms += 1
        self.all_room_codes.add(code)

    def __carve(self, pos):
        self.int_matrix.set_val(pos[0], pos[1], self.getRegion())

    def __canCarve(self, from_pos, direction):
        base_offset = COORD_OFFSET[direction]
        # on dépasse de la matr?
        offset = map(lambda x: x * 3, base_offset)
        offset = tuple(offset)
        dest = (from_pos[0] + offset[0], from_pos[1] + offset[1])

        m_size = self.int_matrix.get_size()
        if not cell_in_range(dest, m_size):
            return False

        # on tente de carve de deja carvé?
        offset = map(lambda x: x * 2, base_offset)
        offset = tuple(offset)
        dest = (from_pos[0] + offset[0], from_pos[1] + offset[1])
        return self.int_matrix.get_val(*dest) is None

    def __growMaze(self, pos):
        last_dir = None
        self.__startRegion()
        self.__carve(pos)
        total_cases_couloir = 1
        self.li_cells_to_explore = [pos]

        while len(self.li_cells_to_explore) > 0:

            index_last = len(self.li_cells_to_explore)
            cell = self.li_cells_to_explore[index_last - 1]

            unmade_possib = list()

            for d in DIRS:
                if self.__canCarve(cell, d):
                    unmade_possib.append(d)

            if len(unmade_possib) > 0:
                if last_dir is None:
                    direction = random.choice(unmade_possib)
                else:
                    if (last_dir not in unmade_possib) or (random.random() < WINDING_FACTOR):
                        direction = random.choice(unmade_possib)
                    else:
                        direction = last_dir

                base_offset = COORD_OFFSET[direction]
                self.__carve((cell[0] + base_offset[0], cell[1] + base_offset[1]))
                cell_creusee = (cell[0] + 2 * base_offset[0], cell[1] + 2 * base_offset[1])
                self.__carve(cell_creusee)
                total_cases_couloir += 2
                if total_cases_couloir <= SEUIL_CASES:
                    self.li_cells_to_explore.append(cell_creusee)
                    last_dir = direction
            else:
                del self.li_cells_to_explore[index_last - 1]
                last_dir = None  # this path ended


# ----------------------------
#   BELOW is an extension by Travis Moy'
#
# *MIT License*
# Copyright (c) 2017 Travis Moy'

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Holds the three angles for each cell. Near is closest to the horizontal/vertical line, and far is furthest.
# Also used for obstructions; for the purposes of obstructions, the center variable is ignored.
class CellAngles(object):
    def __init__(self, near, center, far):
        self.near = near
        self.center = center
        self.far = far

    def __repr__(self):
        return "(near={0} center={1} far={2})".format(self.near, self.center, self.far)


class FOVCalc(object):

    # Changing the radius-fudge changes how smooth the edges of the vision bubble are.
    #
    # RADIUS_FUDGE should always be a value between 0 and 1.
    RADIUS_FUDGE = 1.0 / 3.0

    # If this is False, some cells will unexpectedly be visible.
    #
    # For example, let's say you you have obstructions blocking (0.0 - 0.25) and (.33 - 1.0).
    # A far off cell with (near=0.25, center=0.3125, far=0.375) will have both its near and center unblocked.
    #
    # On certain restrictiveness settings this will mean that it will be visible, but the blocks in front of it will
    # not, which is unexpected and probably not desired.
    #
    # Setting it to True, however, makes the algorithm more restrictive.
    NOT_VISIBLE_BLOCKS_VISION = True

    # Determines how restrictive the algorithm is.
    #
    # 0 - if you have a line to the near, center, or far, it will return as visible
    # 1 - if you have a line to the center and at least one other corner it will return as visible
    # 2 - if you have a line to all the near, center, and far, it will return as visible
    #
    # If any other value is given, it will treat it as a 2.
    RESTRICTIVENESS = 1

    # If VISIBLE_ON_EQUAL is False, an obstruction will obstruct its endpoints. If True, it will not.
    #
    # For example, if there is an obstruction (0.0 - 0.25) and a square at (0.25 - 0.5), the square's near angle will
    # be unobstructed in True, and obstructed on False.
    #
    # Setting this to False will make the algorithm more restrictive.
    VISIBLE_ON_EQUAL = True

    # Parameter func_transparent is a function with the sig: boolean func(x, y)
    # It should return True if the cell is transparent, and False otherwise.
    #
    # Returns a set with all (x, y) tuples visible from the centerpoint.
    def calc_visible_cells_from(self, x_center, y_center, radius, func_transparent):
        cells = self._visible_cells_in_quadrant_from(x_center, y_center, 1, 1, radius, func_transparent)
        cells.update(self._visible_cells_in_quadrant_from(x_center, y_center, 1, -1, radius, func_transparent))
        cells.update(self._visible_cells_in_quadrant_from(x_center, y_center, -1, -1, radius, func_transparent))
        cells.update(self._visible_cells_in_quadrant_from(x_center, y_center, -1, 1, radius, func_transparent))
        cells.add((x_center, y_center))
        return cells

    # Parameters quad_x, quad_y should only be 1 or -1. The combination of the two determines the quadrant.
    # Returns a set of (x, y) tuples.
    def _visible_cells_in_quadrant_from(self, x_center, y_center, quad_x, quad_y, radius, func_transparent):
        cells = self._visible_cells_in_octant_from(x_center, y_center, quad_x, quad_y, radius, func_transparent, True)
        cells.update(self._visible_cells_in_octant_from(x_center, y_center, quad_x, quad_y, radius, func_transparent,
                                                        False))
        return cells

    # Returns a set of (x, y) typles.
    # Utilizes the NOT_VISIBLE_BLOCKS_VISION variable.
    def _visible_cells_in_octant_from(self, x_center, y_center, quad_x, quad_y, radius, func_transparent, is_vertical):
        iteration = 1
        visible_cells = set()
        obstructions = list()

        # End conditions:
        #   iteration > radius
        #   Full obstruction coverage (indicated by one object in the obstruction list covering the full angle from 0
        #      to 1)
        while iteration <= radius and not (len(obstructions) == 1 and
                                           obstructions[0].near == 0.0 and obstructions[0].far == 1.0):
            num_cells_in_row = iteration + 1
            angle_allocation = 1.0 / float(num_cells_in_row)

            # Start at the center (vertical or horizontal line) and step outwards
            for step in range(iteration + 1):
                cell = self._cell_at(x_center, y_center, quad_x, quad_y, step, iteration, is_vertical)

                if self._cell_in_radius(x_center, y_center, cell, radius):
                    cell_angles = CellAngles(near=(float(step) * angle_allocation),
                                             center=(float(step + .5) * angle_allocation),
                                             far=(float(step + 1) * angle_allocation))

                    if self._cell_is_visible(cell_angles, obstructions):
                        visible_cells.add(cell)
                        if not func_transparent(cell[0], cell[1]):
                            obstructions = self._add_obstruction(obstructions, cell_angles)
                    elif self.NOT_VISIBLE_BLOCKS_VISION:
                        obstructions = self._add_obstruction(obstructions, cell_angles)

            iteration += 1

        return visible_cells

    # Returns a (x, y) tuple.
    def _cell_at(self, x_center, y_center, quad_x, quad_y, step, iteration, is_vertical):
        if is_vertical:
            cell = (x_center + step * quad_x, y_center + iteration * quad_y)
        else:
            cell = (x_center + iteration * quad_x, y_center + step * quad_y)
        return cell

    # Returns True/False.
    def _cell_in_radius(self, x_center, y_center, cell, radius):
        cell_distance = math.sqrt((x_center - cell[0]) * (x_center - cell[0]) +
                                  (y_center - cell[1]) * (y_center - cell[1]))
        return cell_distance <= float(radius) + self.RADIUS_FUDGE

    # Returns True/False.
    # Utilizes the VISIBLE_ON_EQUAL and RESTRICTIVENESS variables.
    def _cell_is_visible(self, cell_angles, obstructions):
        near_visible = True
        center_visible = True
        far_visible = True

        for obstruction in obstructions:
            if self.VISIBLE_ON_EQUAL:
                if obstruction.near < cell_angles.near < obstruction.far:
                    near_visible = False
                if obstruction.near < cell_angles.center < obstruction.far:
                    center_visible = False
                if obstruction.near < cell_angles.far < obstruction.far:
                    far_visible = False
            else:
                if obstruction.near <= cell_angles.near <= obstruction.far:
                    near_visible = False
                if obstruction.near <= cell_angles.center <= obstruction.far:
                    center_visible = False
                if obstruction.near <= cell_angles.far <= obstruction.far:
                    far_visible = False

        if self.RESTRICTIVENESS == 0:
            return center_visible or near_visible or far_visible
        elif self.RESTRICTIVENESS == 1:
            return (center_visible and near_visible) or (center_visible and far_visible)
        else:
            return center_visible and near_visible and far_visible

    # Generates a new list by combining all old obstructions with the new one (removing them if they are combined) and
    # adding the resulting obstruction to the list.
    #
    # Returns the generated list.
    def _add_obstruction(self, obstructions, new_obstruction):
        new_object = CellAngles(new_obstruction.near, new_obstruction.center, new_obstruction.far)
        new_list = [o for o in obstructions if not self._combine_obstructions(o, new_object)]
        new_list.append(new_object)
        return new_list

    # Returns True if you combine, False otherwise
    def _combine_obstructions(self, old, new):
        # Pseudo-sort; if their near values are equal, they overlap
        if old.near < new.near:
            low = old
            high = new
        elif new.near < old.near:
            low = new
            high = old
        else:
            new.far = max(old.far, new.far)
            return True

        # If they overlap, combine and return True
        if low.far >= high.near:
            new.near = min(low.near, high.near)
            new.far = max(low.far, high.far)
            return True
        return False
