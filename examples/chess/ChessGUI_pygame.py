import katagames_engine as kengi
from ChessBoard import ChessBoard
from ChessRules import ChessRules
from ScrollingTextBox import ScrollingTextBox
from chess_defs import ChessEvents


W_SIZE = (850, 500)

kengi.bootstrap_e()
pygame = kengi.pygame


def load_img(assetname):
    return pygame.image.load('images/' + assetname)


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

        self.do_paint(board)  # draw board to show end game status
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
                self.pev(ChessEvents.MoveChosen, from_cell=self.fromSquareChosen, to_cell=self.toSquareChosen)
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
