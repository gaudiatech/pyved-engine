from collections import defaultdict

from . import glvars
from .TetColors import TetColors
from .TetPiece import TetPiece
from .ev_types import BlokuEvents


kengi = pyv = glvars.katasdk.pyved_engine
pyg = pyv.pygame


class BagFulloPieces(kengi.Emitter):

    def __init__(self, ref_board):
        super().__init__()

        # bc we need to be able to check if the board is clumped
        self.ref_board = ref_board

        self._avail = list()
        self._refill_bag()

    def __iter__(self):
        return self._avail.__iter__()

    def _refill_bag(self):
        canput_is_proven = False

        for i in range(3):
            obj = TetPiece.gen_random()
            # if i == 0:
            #     obj.move(14, 2)
            # elif i == 1:
            #     obj.move(16, 5)
            # else:
            #     obj.move(18, 8)
            self._avail.append(obj)

            if (not canput_is_proven) and self.ref_board.can_put_anywhere(obj):
                canput_is_proven = True

        self.pev(BlokuEvents.NewPieces)
        if not canput_is_proven:
            self.ref_board.tag_deadend()

    @property
    def content(self):
        return self._avail

    def remove(self, ref_piece):
        self._avail.remove(ref_piece)

        if len(self._avail) > 0:
            for elt in self._avail:
                if self.ref_board.can_put_anywhere(elt):
                    return
            self.ref_board.tag_deadend()
        else:
            self._refill_bag()


class BoardModel(kengi.Emitter):

    SCORE_CAP = 10**6

    def __init__(self, n_columns, n_rows):
        super().__init__()

        self.height = n_rows
        self.width = n_columns
        self.columns = [self.height] * n_columns
        self.score = 0
        self.shadowpiece = None
        self.finalize_ready = False
        self.tiles = defaultdict(lambda: TetColors.Clear)
        self.score = 0
        self.lines = 0
        self.blocked_game = False

    def can_put_anywhere(self, ref_piece):
        for i in range(self.width):
            for j in range(self.height):
                if self.can_put(ref_piece, (i, j)):
                    return True
        return False

    def tag_deadend(self):
        self.blocked_game = True
        print('xxx BLOCKED GAME xxx')
        print('your score is {}'.format(self.score))
        self.pev(BlokuEvents.GameLost)

    def update(self):
        """
        after finalizing a piece (it has been put on the board)
        we NEED to check if there's a flush in
        any column or any line!
        """
        def col_full(col_index):
            for jj in range(self.height):
                if self.tiles[(col_index, jj)] == TetColors.Clear:
                    return False
            return True

        def row_full(row):
            for col in range(self.width):
                if self.tiles[(col, row)] == TetColors.Clear:
                    return False
            return True

        to_be_cleared = set()
        increm_score = 0

        for j in range(10):
            if row_full(j):
                # tag all cells in this row for deletion
                increm_score += 25
                for i in range(self.width):
                    to_be_cleared.add((i, j))

        for i in range(10):
            if col_full(i):
                increm_score += 25
                # tag all cells in this column for deletion
                for j in range(self.height):
                    to_be_cleared.add((i, j))

        if increm_score > 0:
            self.pev(BlokuEvents.LineDestroyed)
            self.upgrade_score(increm_score)
            for zombiecell in to_be_cleared:
                self.tiles[zombiecell] = TetColors.Clear

    def upgrade_score(self, bonus):
        if self.score+bonus < self.SCORE_CAP:
            self.score += bonus
        else:
            self.score = self.SCORE_CAP-1
        self.pev(BlokuEvents.ScoreChanges, score=self.score)

    def set_tile_color(self, x, y, color):
        # assert color != TetColor.CLEAR
        self.tiles[(x, y)] = color
        if color == TetColors.Clear:
            return
        if self.columns[x] > y:
            self.columns[x] = y

    def is_tile_empty(self, x, y):
        return self.tiles[(x, y)] == TetColors.Clear

    def can_put(self, piece_obj, coords_ij):
        sh = piece_obj.shape

        temp = TetPiece(coords_ij[0], coords_ij[1], sh, sh["color"])
        for x, y in temp:
            if x >= self.width:
                return False
            if y >= self.height:
                return False
            if self.tiles[(x, y)] != TetColors.Clear:
                return False

        return True

    def put_piece(self, ref_p, coords_ij):
        shape = ref_p.shape
        self.shadowpiece = TetPiece(coords_ij[0], coords_ij[1], shape, shape["color"])
        self.finalize_piece()

    def finalize_piece(self):
        for x, y in self.shadowpiece:
            self.set_tile_color(x, y, self.shadowpiece.color)

        self.update()
        # self.accu_score()

        self.shadowpiece = None

    def met_a_jour_vue(self, v):
        v.clear()

        for (x, y), color in self.tiles.items():
            v.render_tile(x, y, color)

        if self.shadowpiece is not None:
            self.shadowpiece.savecolor_in_grid(v)


class TetrominoSpr(pyg.sprite.Sprite):
    cls_cpt = 0

    def __init__(self, ref_piece):
        super().__init__()
        req_size = TetrominoSpr._calc_req_img_size(ref_piece)
        self.ref_piece = ref_piece

        ck_pink = (0xff, 0x00, 0xff)

        self.image = pyg.surface.Surface(req_size)  # will never be blit to screen, this is only for collision detect

        #self.image.fill(ck_pink)
        #self.image.set_colorkey(ck_pink)

        # self.shadow_img = pyg.surface.Surface(req_size)
        #self.shadow_img.fill(ck_pink)
        #self.shadow_img.set_colorkey(ck_pink)

        # disabled du to bug webctx (draw primitives on pyg.Surf)
        # TetrominoSpr.adhoc_render(self.image, ref_piece)
        # TetrominoSpr.adhoc_render(self.shadow_img, ref_piece, TetColors.Gray)

        self.rect = self.image.get_rect()
        self.dragged = False
        self.mouse_offset = None
        self.__class__.cls_cpt = (self.__class__.cls_cpt + 1) % 3

    def paint_shadow(self, refscreen, pair_xy):
        TetrominoSpr.adhoc_render(refscreen, self.ref_piece, color=TetColors.Gray, pos=pair_xy)

    def paint_sprite(self, refscreen):
        TetrominoSpr.adhoc_render(refscreen, self.ref_piece, color=TetColors.Pink, pos=self.rect.topleft)

    def update(self, *args, **kwargs) -> None:
        if self.dragged:
            mx, my = pyv.proj_to_vscreen(pyg.mouse.get_pos())
            new_pos = [
                mx + self.mouse_offset[0],
                my + self.mouse_offset[1],
            ]
            self.rect.topleft = new_pos

    @staticmethod
    def draw_lilsquare(ecran, x, y, chosencolor):
        sq_size = glvars.SQ_SIZE
        pg_color = glvars.colour_map[chosencolor]
        bd_size = glvars.BORDER_SIZE

        # below: a dirty fix en attendant que emulateur pygame evolue!
        # bd_color = pg_color - glvars.border_fade_colour

        # TODO remettre la ligne davant qd emu- pygame est GOOD!
        bd_color = [pg_color[0] - 16, pg_color[1] - 16, pg_color[2] - 16]

        outer_rect = (x, y, sq_size, sq_size)
        inner_rect = (x + bd_size, y + bd_size, sq_size - bd_size * 2, sq_size - bd_size * 2)
        pyg.draw.rect(ecran, bd_color, outer_rect, 0)
        pyg.draw.rect(ecran, pg_color, inner_rect, 0)

    @staticmethod
    def adhoc_render(targ_surface, ref_tpiece, color=None, pos=None):
        # render Tetromino on a surface
        sq_li = ref_tpiece.shape["tiles"]
        adhoc_color = ref_tpiece.color
        if color is not None:
            adhoc_color = color

        xbase, ybase = 0, 0
        if pos:
            xbase += pos[0]
            ybase += pos[1]
        for sq in sq_li:
            TetrominoSpr.draw_lilsquare(
                targ_surface, xbase + glvars.SQ_SIZE * sq[0], ybase + glvars.SQ_SIZE * sq[1], adhoc_color
            )

    @staticmethod
    def _calc_req_img_size(ref_piece):
        dimx = (1+int(ref_piece.shape["x_adj"]))*glvars.SQ_SIZE
        dimy = (1+int(ref_piece.shape["y_adj"]))*glvars.SQ_SIZE
        return dimx, dimy


class PuzzleView(pyv.EvListener):

    BOARD_BORDER_SIZE = 5
    SCORE_PADDING = 5
    last_instance = None

    def __init__(self, board, avail, orgpoint):
        super().__init__()

        PuzzleView.last_instance = self  # used for debugging only
        self._hl_cell = None  # marquer la case en rouge, utile au debug
        self.shadow_spr_ij = None  # indique ou drop l'ombre

        # - - where is the board rel. to the whole screen - -
        self.org_point = orgpoint

        # save parameters
        self.boardmodel = board

        self._bag_model = avail

        self.font_color = glvars.colors['c_lightpurple']
        self.bgcolor = glvars.colors['c_purple']

        # dico de spr
        self._sprites = dict()
        self._create_adhoc_sprites()

        # - base
        self.rows = None
        self.clear()  # init attribute .rows
        self.curr_dragged = None

        self.scr = pyv.get_surface()

    def on_event(self, ev):
        if ev.type == pyv.EngineEvTypes.Paint:

            for spr in self._sprites.values():
                spr.update()
            self.do_paint(ev.screen)

        elif ev.type == pyv.EngineEvTypes.Mousemotion:
            if self.curr_dragged:
                x, y = pyv.proj_to_vscreen(ev.pos)
                pos_topleft = (
                    x + self.curr_dragged.mouse_offset[0],
                    y + self.curr_dragged.mouse_offset[1]
                )
                tmp = self.to_gamecoords(pos_topleft)

                piece = self.get_dragged_piece_obj()
                found_loc = False
                if tmp is not None:
                    if self.boardmodel.can_put(piece, tmp):
                        self.shadow_spr_ij = tmp
                        found_loc = True
                if not found_loc:
                    self.shadow_spr_ij = None

        elif ev.type == pyv.EngineEvTypes.Mousedown:
            mpos = pyv.proj_to_vscreen(ev.pos)

            for tmp in self._sprites.values():
                if tmp.rect.collidepoint(mpos):
                    tmp.pos_jadis = tmp.rect.topleft
                    tmp.dragged = True
                    mx, my = mpos
                    a, b = tmp.rect.topleft
                    tmp.mouse_offset = a - mx, b - my
                    self.curr_dragged = tmp
                    break

        elif (ev.type == pyv.EngineEvTypes.Mouseup) and self.curr_dragged:
            self._proc_mouse_up( pyv.proj_to_vscreen(ev.pos))
            self.curr_dragged = None
            self.shadow_spr_ij = None

        elif ev.type == BlokuEvents.NewPieces:
            self._create_adhoc_sprites()

    def _create_adhoc_sprites(self):
        for idx, piece_obj in enumerate(self._bag_model):
            key = piece_obj
            self._sprites[key] = TetrominoSpr(piece_obj)

        ordered_pieces = list()
        for k in self._sprites.keys():
            s = len(ordered_pieces)
            if not s:  # empty list
                ordered_pieces.append(k)
            else:
                cpt = 0
                while (cpt < s) and k.get_area() > ordered_pieces[cpt].get_area():
                    cpt += 1
                ordered_pieces.insert(cpt, k)

        # position sprites so we have more chances to see it clear
        csiz = glvars.SQ_SIZE
        refx, refy = self.org_point[0] + self.width*csiz, self.org_point[1]

        for idx, piece_obj in enumerate(ordered_pieces):
            tmp0 = refx + (1+3*idx) * csiz
            tmp1 = refy + 3*idx*csiz
            self._sprites[piece_obj].rect.topleft = (tmp0, tmp1)

    def get_dragged_piece_obj(self):
        if self.curr_dragged is None:
            return None
        else:
            for k, v in self._sprites.items():  # find key that corresponds to self.curr_dragged
                if v == self.curr_dragged:
                    return k

    def _proc_mouse_up(self, mouse_pos):
        drag_sprite = self.curr_dragged
        piece_obj = self.get_dragged_piece_obj()

        pos_topleft = (
            mouse_pos[0] + self.curr_dragged.mouse_offset[0],
            mouse_pos[1] + self.curr_dragged.mouse_offset[1]
        )
        # dim_spr = drag_sprite.image.get_size()
        # pos_center_square = (
        #     int(pos_of_piece_center[0] - (dim_spr[0]/2) + SQ_SIZE/2),
        #     int(pos_of_piece_center[1] - (dim_spr[1]/2) + SQ_SIZE/2),
        # )

        coords = self.to_gamecoords(pos_topleft)
        must_reset_spr = True

        if coords:
            # TETROMINO SPR WAS DROPPED!
            # test if its possible
            # - debug
            # print('found to be in the grid')

            if self.boardmodel.can_put(piece_obj, coords):
                # - debug
                # print('coords found but cant drop')
                self.boardmodel.put_piece(piece_obj, coords)
                self._bag_model.remove(piece_obj)
                del self._sprites[piece_obj]
                must_reset_spr = False

        if must_reset_spr:
            drag_sprite.rect.topleft = drag_sprite.pos_jadis
        drag_sprite.dragged = False

    def highlight_cell(self, ij=None):
        self._hl_cell = ij

    @staticmethod
    def edist(p1, p2):
        return

    def to_gamecoords(self, xy_pair):
        a, b = -self.org_point[0], -self.org_point[1]
        a += xy_pair[0]
        b += xy_pair[1]
        if a < 0 or b < 0:
            return None
        else:
            a /= glvars.SQ_SIZE
            b /= glvars.SQ_SIZE
            if a >= self.boardmodel.width or b >= self.boardmodel.height:
                return None
            else:
                return int(a), int(b)

    def clear(self):
        self.rows = [
            [TetColors.Clear] * self.height for _ in range(self.width)
        ]

    def render_tile(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.rows[x][y] = color

    # --------------------------------------------------------
    #  THREE METHODS USEFUL FOR GRAPHIC UPDATE
    # --------------------------------------------------------
    def do_paint(self, ref_screen, updatefrom_model=True):
        if updatefrom_model:
            self.boardmodel.met_a_jour_vue(self)
            # TODO faire en sorte que vue tjr à jour
            # TODO faire en sorte que la vue se dessine tt seule (et pas quil faille que le ctrl lui dise qd le faire)

        # if self.show_action is not None:
        #     self.show_action()

        ref_screen.fill(self.bgcolor)
        self.draw_board(ref_screen)

    def draw_board(self, ecran):
        board_color = glvars.colour_map[TetColors.Clear]

        x_start = self.org_point[0]
        y_start = self.org_point[1]

        x, y = x_start, y_start
        cst = glvars.SQ_SIZE
        board_rect = (x, y, self.width * cst, self.height * cst)
        pyg.draw.rect(ecran, board_color, board_rect)

        for col in self.rows:
            for item in col:
                TetrominoSpr.draw_lilsquare(ecran, x, y, item)
                y += cst
            x += cst
            y = y_start

        if self.shadow_spr_ij:
            tmpi, tmpj = self.shadow_spr_ij
            self.curr_dragged.paint_shadow(
                ecran,
                (self.org_point[0] + cst * tmpi, self.org_point[1] + cst * tmpj)
            )
            # tmpi, tmpj = self.shadow_spr_ij
            # self.scr.blit(
            #     self.curr_dragged.shadow_img,
            #     (self.org_point[0] + cst * tmpi,
            #      self.org_point[1] + cst * tmpj)
            # )

        self.draw_grid(ecran)

        if self._hl_cell:
            i, j = self._hl_cell
            cst = glvars.SQ_SIZE
            pyg.draw.rect(
                ecran, (255, 0, 0),
                (self.org_point[0]+i*cst, self.org_point[1]+j*cst, cst, cst),
                1
            )

        # (hotfix backend 0.2.0 bug)
        pyg.draw.line(ecran, glvars.colour_map[TetColors.Pink], [0, 0], (2, 0), width=1)

        # dessin des pieces en rab, dapres les sprites!
        for spr in self._sprites.values():
            # webcxt bug, so we replace:
            # ecran.blit(spr.image, spr.rect.topleft)
            # by...
            spr.paint_sprite(ecran)

    def draw_grid(self, screen_ref):
        """
        Draw black lines! Fat grid
        """
        linecolor = (0x74, 0x54, 0x54)
        thickness = 1
        cst = glvars.SQ_SIZE
        for i in range(self.width+1):
            xline = cst*i
            org = (self.org_point[0]+xline, self.org_point[1])
            dest = (self.org_point[0]+xline, self.org_point[1]+self.px_height)
            pyg.draw.line(screen_ref, linecolor, org, dest, thickness)

            for j in range(self.height+1):
                yline = cst*j
                org = (self.org_point[0], self.org_point[1]+yline)
                dest = (self.org_point[0]+self.px_width, self.org_point[1]+yline)
                pyg.draw.line(screen_ref, linecolor, org, dest, thickness)

    # --------------------------------------------------------
    #  PROPERTIES
    # --------------------------------------------------------
    @property
    def width(self):
        return self.boardmodel.width

    @property
    def px_width(self):
        return self.boardmodel.width * glvars.SQ_SIZE

    @property
    def height(self):
        return self.boardmodel.height

    @property
    def px_height(self):
        return self.boardmodel.height * glvars.SQ_SIZE


class PuzzleCtrl(pyv.EvListener):

    def __init__(self, board_mod, avail, ref_view, view_score):
        super().__init__()
        self.view2 = view_score
        self.boardmodel = board_mod
        self._avail = avail
        self.view = ref_view
        self.game_over = False
        self.show_action = None
        self._score_sent = False
        self._rdy_to_exit = False

    def flag_games_over(self):
        self.game_over = True
        self._score_sent = False
        self._rdy_to_exit = False

    # ---------------------------------------
    #  GESTION EV. COREMON ENG.
    # ---------------------------------------
    def on_event(self, ev):
        # elif ev.type == kevent.EngineEvTypes.Update:
        #     if self.game_over:
        #         if not self._score_sent:
        #             pass
        #             # TODO fix later
        #             # katapi.push_score(
        #             #     glvars.acc_id, glvars.username, glvars.num_challenge, self.boardmodel.score
        #             # )
        #             self._score_sent = True

        if ev.type == BlokuEvents.GameLost:
            self.flag_games_over()
            self.view2.flag_game_over = True
            self._rdy_to_exit = True


        elif ev.type == pyv.EngineEvTypes.Keydown:
            if ev.key == pyv.pygame.K_RETURN and self._rdy_to_exit:
                self.pev(pyv.EngineEvTypes.StatePop)
