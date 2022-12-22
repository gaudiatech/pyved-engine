import chdefs
import katagames_engine as kengi
from ChessBoard import ChessBoard
from ChessRules import ChessRules
from players import ChessAI_random, ChessAI_offense, ChessAI_defense, ChessPlayer


# - alias
pygame = kengi.pygame


# constants:
PAUSE_SEC = 3
W_SIZE = (850, 500)


def load_img(assetname):
    return pygame.image.load('images/' + assetname)


class ChessgameModel:
    def __init__(self):
        # 0 for normal board setup; see ChessBoard class for other options (testing purposes)
        # e.g. the debug mode can use arg 2 instead of 0
        self.board = ChessBoard(0)
        self.rules = ChessRules()

        self.players = None
        self._initplayers()

    def _initplayers(self):
        default_config = (
            'Player1', 'white', 'human',
            'AI', 'black', 'defenseAI'
        )
        (player1Name, player1Color, player1Type, player2Name, player2Color, player2Type) = default_config
        # replace default config playertypes by what has been stored in chdefs
        player1Type, player2Type = chdefs.pltype1, chdefs.pltype2
        print('**', player1Type, player2Type)

        self.players = [0, 0]
        if player1Type == 'human':
            self.players[0] = ChessPlayer(player1Name, player1Color)
        elif player1Type == 'randomAI':
            self.players[0] = ChessAI_random(player1Name, player1Color)
        elif player1Type == 'defenseAI':
            self.players[0] = ChessAI_defense(player1Name, player1Color)
        elif player1Type == 'offenseAI':
            self.players[0] = ChessAI_offense(player1Name, player1Color)
        if player2Type == 'human':
            self.players[1] = ChessPlayer(player2Name, player2Color)
        elif player2Type == 'randomAI':
            self.players[1] = ChessAI_random(player2Name, player2Color)
        elif player2Type == 'defenseAI':
            self.players[1] = ChessAI_defense(player2Name, player2Color)
        elif player2Type == 'offenseAI':
            self.players[1] = ChessAI_offense(player2Name, player2Color)
        if 'AI' in self.players[0].type and 'AI' in self.players[1].type:
            AIvsAI = True
        else:
            AIvsAI = False
        if PAUSE_SEC > 0:
            AIpause = True
            AIpauseSeconds = int(PAUSE_SEC)
        else:
            AIpause = False


class ChessGameView(kengi.EvListener):
    BG_COLOR = (125, 110, 120)  #  '#06170e' # dark green  #

    OFFSET_X = 64
    OFFSET_Y = 175

    def __init__(self, screenref):
        super().__init__()

        self.Rules = ChessRules()
        self.board = None  # update from outside
        self.curr_color = 'white'  # player active, updated from outside

        self._fluo_squares = None  # qd qq chose est select ->affiche ou on peut bouger
        self.possibleDestinations = None

        # gui
        self.fromSquareChosen = self.toSquareChosen = None
        self._sortie_subloop = self._sortie_subloop2 = None

        # self.textBox = ScrollingTextBox(self.screen, 525, 825, 50, 450)
        # -* Hacking begins *-
        self.textBox = kengi.console.CustomConsole(screenref, (self.OFFSET_X, 4, 640, 133))
        self.textBox.active = True
        self.textBox.bg_color = self.BG_COLOR  # customize console
        self.textBox.font_size = 25
        # self.textBox.Add = extAdd
        self.textBox.Add = self.textBox.output
        # -* Hacking done *-

        self._preload_assets()
        self.fontDefault = pygame.font.Font(None, 20)
        self.ready_to_quit = False

    def _preload_assets(self):
        self.square_size = 100
        self.white_square = load_img("white_square.png")
        self.brown_square = load_img("brown_square.png")
        self.cyan_square = load_img("cyan_square.png")
        self.black_pawn = load_img("Chess_tile_pd.png")
        self.black_pawn = pygame.transform.scale(self.black_pawn, (self.square_size, self.square_size))
        self.black_rook = load_img("Chess_tile_rd.png")
        self.black_rook = pygame.transform.scale(self.black_rook, (self.square_size, self.square_size))
        self.black_knight = load_img("Chess_tile_nd.png")
        self.black_knight = pygame.transform.scale(self.black_knight, (self.square_size, self.square_size))
        self.black_bishop = load_img("Chess_tile_bd.png")
        self.black_bishop = pygame.transform.scale(self.black_bishop, (self.square_size, self.square_size))
        self.black_king = load_img("Chess_tile_kd.png")
        self.black_king = pygame.transform.scale(self.black_king, (self.square_size, self.square_size))
        self.black_queen = load_img("Chess_tile_qd.png")
        self.black_queen = pygame.transform.scale(self.black_queen, (self.square_size, self.square_size))
        self.white_pawn = load_img("Chess_tile_pl.png")
        self.white_pawn = pygame.transform.scale(self.white_pawn, (self.square_size, self.square_size))
        self.white_rook = load_img("Chess_tile_rl.png")
        self.white_rook = pygame.transform.scale(self.white_rook, (self.square_size, self.square_size))
        self.white_knight = load_img("Chess_tile_nl.png")
        self.white_knight = pygame.transform.scale(self.white_knight, (self.square_size, self.square_size))
        self.white_bishop = load_img("Chess_tile_bl.png")
        self.white_bishop = pygame.transform.scale(self.white_bishop, (self.square_size, self.square_size))
        self.white_king = load_img("Chess_tile_kl.png")
        self.white_king = pygame.transform.scale(self.white_king, (self.square_size, self.square_size))
        self.white_queen = load_img("Chess_tile_ql.png")
        self.white_queen = pygame.transform.scale(self.white_queen, (self.square_size, self.square_size))
        self.square_size = 50

    def PrintMessage(self, message):
        # prints a string to the area to the right of the board
        # print('envoi [{}] ds la console...'.format(message))
        self.textBox.Add(message)
        # self.textBox.draw()

    def ConvertToScreenCoords(self, chessSquareTuple):
        # converts a (row,col) chessSquare into the pixel location of the upper-left corner of the square
        (row, col) = chessSquareTuple
        screenX = self.OFFSET_X + col * self.square_size
        screenY = self.OFFSET_Y + row * self.square_size
        return screenX, screenY

    def ConvertToChessCoords(self, screenPositionTuple):
        # converts a screen pixel location (X,Y) into a chessSquare tuple (row,col)
        # x is horizontal, y is vertical
        # (x=0,y=0) is upper-left corner of the screen
        (X, Y) = screenPositionTuple
        row = (Y - self.OFFSET_Y) / self.square_size
        col = (X - self.OFFSET_X) / self.square_size
        return int(row), int(col)

    def drawboard(self, scrsurf, board):
        scrsurf.fill(self.BG_COLOR)

        boardSize = len(board)  # should be always 8, but here we can avoid magic numbers

        # draw blank board
        current_square = 0
        for r in range(boardSize):
            for c in range(boardSize):
                (screenX, screenY) = self.ConvertToScreenCoords((r, c))
                if current_square:
                    scrsurf.blit(self.brown_square, (screenX, screenY))
                    current_square = (current_square + 1) % 2
                else:
                    scrsurf.blit(self.white_square, (screenX, screenY))
                    current_square = (current_square + 1) % 2
            current_square = (current_square + 1) % 2

        # draw row/column labels around the edge of the board
        chessboard_obj = ChessBoard(0)  # need a dummy object to access some of ChessBoard's methods....
        color = (255, 255, 255)  # white
        antialias = 1

        # top and bottom - display cols
        for c in range(boardSize):
            for r in [-1, boardSize]:
                (screenX, screenY) = self.ConvertToScreenCoords((r, c))
                screenX = screenX + self.square_size / 2
                screenY = screenY + self.square_size / 2
                notation = chessboard_obj.ConvertToAlgebraicNotation_col(c)
                renderedLine = self.fontDefault.render(notation, antialias, color)
                scrsurf.blit(renderedLine, (screenX, screenY))

        # left and right - display rows
        for r in range(boardSize):
            for c in [-1, boardSize]:
                (screenX, screenY) = self.ConvertToScreenCoords((r, c))
                screenX = screenX + self.square_size / 2
                screenY = screenY + self.square_size / 2
                notation = chessboard_obj.ConvertToAlgebraicNotation_row(r)
                renderedLine = self.fontDefault.render(notation, antialias, color)
                scrsurf.blit(renderedLine, (screenX, screenY))

        # highlight squares if specified
        if self._fluo_squares is not None:
            for e in self._fluo_squares:
                (screenX, screenY) = self.ConvertToScreenCoords(e)
                scrsurf.blit(self.cyan_square, (screenX, screenY))

        self.textBox.draw()

        # draw pieces
        for r in range(boardSize):
            for c in range(boardSize):
                if board[r][c] == 'bP':
                    self.dessin_piece_centree(scrsurf, self.black_pawn, (r, c))

                if board[r][c] == 'bR':
                    self.dessin_piece_centree(scrsurf, self.black_rook, (r, c))

                if board[r][c] == 'bT':
                    self.dessin_piece_centree(scrsurf, self.black_knight, (r, c))

                if board[r][c] == 'bB':
                    self.dessin_piece_centree(scrsurf, self.black_bishop, (r, c), -13)

                if board[r][c] == 'bQ':
                    self.dessin_piece_centree(scrsurf, self.black_queen, (r, c))

                if board[r][c] == 'bK':
                    self.dessin_piece_centree(scrsurf, self.black_king, (r, c), -18)

                if board[r][c] == 'wP':
                    self.dessin_piece_centree(scrsurf, self.white_pawn, (r, c))

                if board[r][c] == 'wR':
                    self.dessin_piece_centree(scrsurf, self.white_rook, (r, c))

                if board[r][c] == 'wT':
                    self.dessin_piece_centree(scrsurf, self.white_knight, (r, c))

                if board[r][c] == 'wB':
                    self.dessin_piece_centree(scrsurf, self.white_bishop, (r, c), -13)

                if board[r][c] == 'wQ':
                    self.dessin_piece_centree(scrsurf, self.white_queen, (r, c))

                if board[r][c] == 'wK':
                    self.dessin_piece_centree(scrsurf, self.white_king, (r, c), -18)

    def EndGame(self, board):
        if not self.ready_to_quit:
            self.PrintMessage("Press any key to exit.")
            self.ready_to_quit = True

        self.drawboard(kengi.get_surface(), board)  # draw board to show end game status
        # TODO remove this flip
        # kengi.flip()

    def _gere_square_chosen(self, board):
        fromSquareChosen = []
        toSquareChosen = 0
        squareClicked = self.fromSquareChosen
        currentColor = None
        fromTuple = (0, 0)
        if not fromSquareChosen and not toSquareChosen:
            # self.do_paint(self.screen, board)
            if squareClicked:
                (r, c) = squareClicked
                if currentColor == 'black' and 'b' in board[r][c]:
                    if len(self.Rules.GetListOfValidMoves(board, currentColor, squareClicked)) > 0:
                        fromSquareChosen = 1
                        fromTuple = squareClicked
                elif currentColor == 'white' and 'w' in board[r][c]:
                    if len(self.Rules.GetListOfValidMoves(board, currentColor, squareClicked)) > 0:
                        fromSquareChosen = 1
                        fromTuple = squareClicked
        elif fromSquareChosen and not toSquareChosen:
            if len(squareClicked):
                (r, c) = squareClicked
                if squareClicked in self.possibleDestinations:
                    toSquareChosen = 1
                    toTuple = squareClicked
                elif currentColor == 'black' and 'b' in board[r][c]:
                    if squareClicked == fromTuple:
                        fromSquareChosen = 0
                    elif len(self.Rules.GetListOfValidMoves(board, currentColor, squareClicked)) > 0:
                        fromSquareChosen = 1
                        fromTuple = squareClicked
                    else:
                        fromSquareChosen = 0  # piece is of own color, but no possible moves
                elif currentColor == 'white' and 'w' in board[r][c]:
                    if squareClicked == fromTuple:
                        fromSquareChosen = 0
                    elif len(self.Rules.GetListOfValidMoves(board, currentColor, squareClicked)) > 0:
                        fromSquareChosen = 1
                        fromTuple = squareClicked
                    else:
                        fromSquareChosen = 0
                else:  # blank square or opposite color piece not in possible destinations clicked
                    fromSquareChosen = 0

        if fromSquareChosen or toSquareChosen:
            self._sortie_subloop = (fromSquareChosen, toSquareChosen)

    def forward_mouseev(self, ev):
        """
        format save to self._sortie_subloop:
        (from_row,from_col), (to_row,to_col)
        """

        board = self.board
        currcolor = self.curr_color

        (mouseX, mouseY) = ev.pos
        squareClicked = self.ConvertToChessCoords((mouseX, mouseY))
        if (not (0 <= squareClicked[0] <= 7)) or (not(0 <= squareClicked[1] <= 7)):  # TODO internaliser ds convert..
            # set all None, bc its not a valid chess square
            self._fluo_squares = None
            self.possibleDestinations = None
            self.fromSquareChosen = None
            return

        if not self.fromSquareChosen:
            self.fromSquareChosen = squareClicked
            fromTuple = tuple(squareClicked)
            # TODO set fromTuple properly

            self.possibleDestinations = self.Rules.GetListOfValidMoves(board.GetState(), currcolor, fromTuple)
            if len(self.possibleDestinations):
                self._fluo_squares = list(self.possibleDestinations)
            else:
                self._fluo_squares = None

        # self._gere_square_chosen(board.GetState())
        else:
            if squareClicked in self.possibleDestinations:
                self.toSquareChosen = squareClicked
                self.pev(
                    chdefs.ChessEvents.MoveChosen, from_cell=self.fromSquareChosen, to_cell=self.toSquareChosen
                )
            self._fluo_squares = None
            self.possibleDestinations = None
            self.fromSquareChosen = None

    def dessin_piece_centree(self, screenref, black_pawn, case, voffset=-10):
        (screenX, screenY) = self.ConvertToScreenCoords(case)
        # on souhaite que le centre de la case & le centre de l'image coincident
        # Pour cela, on calcule le coin en haut à gauche qui va bien...
        delta = self.square_size // 2
        centre_case = (screenX + delta, screenY + delta)
        tmp = black_pawn.get_size()
        goodx = centre_case[0] - tmp[0] // 2
        goody = centre_case[1] - tmp[1] // 2
        goody += voffset
        screenref.blit(black_pawn, (goodx, goody))


class ChessTicker(kengi.EvListener):
    def __init__(self, refmod, refview):
        super().__init__()
        self.model = refmod
        self.refview = refview
        self.refview.board = refmod.board
        self.stored_human_input = None  # when smth has been played!
        self._curr_pl_idx = 0
        self._turn_count = 0
        self.endgame_msg_added = False
        self.board_st = refmod.board.GetState()
        self.ready_to_quit = False
        self.endgame_msg_added = False

    def on_move_chosen(self, ev):  # as defined in ChessEvents
        self.stored_human_input = [ev.from_cell, ev.to_cell]
        # print('-- STORING - -', self.stored_human_input)

    def on_keydown(self, ev):
        if ev.key == kengi.pygame.K_ESCAPE:
            self.pev(kengi.EngineEvTypes.Gameover)
        elif self.ready_to_quit:
            self.pev(kengi.EngineEvTypes.StatePop)

    def on_mousedown(self, ev):
        self.refview.forward_mouseev(ev)

    def on_gameover(self, ev):
        """
        maybe there are other ways to exit than just pressing ESC...
        in this method, we update the game object
        """
        chdefs.ref_game_obj.gameover = True

    def on_quit(self, ev):  # press quit button
        self.on_gameover(ev)

    def on_paint(self, ev):
        self.refview.drawboard(ev.screen, self.board_st)

    def on_update(self, ev):
        board_st = self.board_st
        players = self.model.players
        curr_player = players[self._curr_pl_idx]

        if self.ready_to_quit:
            # --- manage end game ---
            if not self.endgame_msg_added:
                self.refview.PrintMessage("CHECKMATE!")
                winnerIndex = (self._curr_pl_idx + 1) % 2
                self.refview.PrintMessage(
                    players[winnerIndex].name + " (" + curr_player.color + ") won the game!")
                self.endgame_msg_added = True
                self.refview.EndGame(self.board_st)
            return

        # -- the problem with THAT type of code is that it BLOCKS the soft!
        # if player[currentPlayerIndex].type == 'AI':
        #     moveTuple = player[currentPlayerIndex].GetMove(board.GetState(), currentColor)
        # else:
        #     moveTuple = Gui.GetPlayerInput(board_st, currentColor)
        # TODO repair human vs A.I. play

        move_report = None

        if curr_player.type == 'human':
            moveTuple = self.stored_human_input
            if moveTuple:
                move_report = self.model.board.move_piece(moveTuple)
                # moveReport = string like "White Bishop moves from A1 to C3" (+) "and captures ___!"
                self.stored_human_input = None

        else:
            tmp_ai_move = curr_player.GetMove(board_st, curr_player.color)
            move_report = self.model.board.move_piece(tmp_ai_move)

        # self.refview.drawboard(gl_screen_ref, board_st)

        if move_report:  # smth has been played!
            self.refview.PrintMessage(move_report)
            # this will cause the currentPlayerIndex to toggle between 1 and 0

            # -- iterate game --
            self._curr_pl_idx = (self._curr_pl_idx + 1) % 2
            curr_player = players[self._curr_pl_idx]
            self.refview.curr_color = ['white', 'black'][self._curr_pl_idx]

            # TODO repair feat.
            # if AIvsAI and AIpause:
            #     time.sleep(AIpauseSeconds)

            if self.model.rules.IsCheckmate(self.board_st, curr_player.color):
                self.ready_to_quit = True

            currentColor = curr_player.color
            # hardcoded so that player 1 is always white
            if currentColor == 'white':
                self._turn_count = self._turn_count + 1
            self.refview.PrintMessage("")
            baseMsg = "TURN %s - %s (%s)" % (str(self._turn_count), curr_player.name, currentColor)
            self.refview.PrintMessage("--%s--" % baseMsg)
            if self.model.rules.IsInCheck(board_st, currentColor):
                suffx = '{} ({}) is in check'.format(curr_player.name, curr_player.color)
                self.refview.PrintMessage("Warning..." + suffx)


class ChessmatchState(kengi.BaseGameState):
    # bind state_id to class is done automatically by kengi (part 1 /2)

    def enter(self):
        self.m = ChessgameModel()

        pygamegui = self.v = ChessGameView(kengi.get_surface())

        self.t = ChessTicker(self.m, pygamegui)
        self.t.turn_on()

    def release(self):
        for evl in (self.v, self.t):
            evl.turn_off()


# ----------------
#  if need to test/debug the pygame view
# ----------------

# if __name__ == "__main__":
#     # try out some development / testing stuff if this file is run directly
#     testBoard = [['bR', 'bT', 'bB', 'bQ', 'bK', 'bB', 'bT', 'bR'], \
#                  ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'], \
#                  ['e', 'e', 'e', 'e', 'e', 'e', 'e', 'e'], \
#                  ['e', 'e', 'e', 'e', 'e', 'e', 'e', 'e'], \
#                  ['e', 'e', 'e', 'e', 'e', 'e', 'e', 'e'], \
#                  ['e', 'e', 'e', 'e', 'e', 'e', 'e', 'e'], \
#                  ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'], \
#                  ['wR', 'wT', 'wB', 'wQ', 'wK', 'wB', 'wT', 'wR']]
#     validSquares = [(5, 2), (1, 1), (1, 5), (7, 6)]
#     game = ChessGUI_pygame()
#     game.Draw(testBoard, validSquares)
#     game.TestRoutine()
