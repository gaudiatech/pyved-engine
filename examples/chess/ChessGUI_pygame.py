import katagames_engine as kengi
from ChessBoard import ChessBoard
from ChessRules import ChessRules
from ScrollingTextBox import ScrollingTextBox


W_SIZE = (850, 500)

kengi.bootstrap_e()
pygame = kengi.pygame


def load_img(assetname):
    return pygame.image.load('images/' + assetname)


class ChessGameView:
    def __init__(self, scr_ref):
        self.Rules = ChessRules()
        self.screen = scr_ref
        self.boardStart_x = 50
        self.boardStart_y = 50
        self.textBox = ScrollingTextBox(self.screen, 525, 825, 50, 450)
        self._preload_assets()
        self.fontDefault = pygame.font.Font(None, 20)

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
        self.textBox.Add(message)
        self.textBox.Draw()

    def ConvertToScreenCoords(self, chessSquareTuple):
        # converts a (row,col) chessSquare into the pixel location of the upper-left corner of the square
        (row, col) = chessSquareTuple
        screenX = self.boardStart_x + col * self.square_size
        screenY = self.boardStart_y + row * self.square_size
        return (screenX, screenY)

    def ConvertToChessCoords(self, screenPositionTuple):
        # converts a screen pixel location (X,Y) into a chessSquare tuple (row,col)
        # x is horizontal, y is vertical
        # (x=0,y=0) is upper-left corner of the screen
        (X, Y) = screenPositionTuple
        row = (Y - self.boardStart_y) / self.square_size
        col = (X - self.boardStart_x) / self.square_size
        return int(row), int(col)

    def do_paint(self, board, highlightSquares=None):
        self.screen.fill((125, 110, 120))

        #  TODO rétablir textbox !
        #self.textBox.Draw()
        boardSize = len(board)  # should be always 8, but here we can avoid magic numbers

        # draw blank board
        current_square = 0
        for r in range(boardSize):
            for c in range(boardSize):
                (screenX, screenY) = self.ConvertToScreenCoords((r, c))
                if current_square:
                    self.screen.blit(self.brown_square, (screenX, screenY))
                    current_square = (current_square + 1) % 2
                else:
                    self.screen.blit(self.white_square, (screenX, screenY))
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
                self.screen.blit(renderedLine, (screenX, screenY))

        # left and right - display rows
        for r in range(boardSize):
            for c in [-1, boardSize]:
                (screenX, screenY) = self.ConvertToScreenCoords((r, c))
                screenX = screenX + self.square_size / 2
                screenY = screenY + self.square_size / 2
                notation = chessboard_obj.ConvertToAlgebraicNotation_row(r)
                renderedLine = self.fontDefault.render(notation, antialias, color)
                self.screen.blit(renderedLine, (screenX, screenY))

        # highlight squares if specified
        if highlightSquares:
            for square in highlightSquares:
                (screenX, screenY) = self.ConvertToScreenCoords(square)
                self.screen.blit(self.cyan_square, (screenX, screenY))

        # draw pieces
        for r in range(boardSize):
            for c in range(boardSize):
                if board[r][c] == 'bP':
                    self.dessin_piece_centree(self.black_pawn, (r, c))

                if board[r][c] == 'bR':
                    self.dessin_piece_centree(self.black_rook, (r, c))

                if board[r][c] == 'bT':
                    self.dessin_piece_centree(self.black_knight, (r, c))

                if board[r][c] == 'bB':
                    self.dessin_piece_centree(self.black_bishop, (r, c), -13)

                if board[r][c] == 'bQ':
                    self.dessin_piece_centree(self.black_queen, (r, c))

                if board[r][c] == 'bK':
                    self.dessin_piece_centree(self.black_king, (r, c), -18)

                if board[r][c] == 'wP':
                    self.dessin_piece_centree(self.white_pawn, (r, c))

                if board[r][c] == 'wR':
                    self.dessin_piece_centree(self.white_rook, (r, c))

                if board[r][c] == 'wT':
                    self.dessin_piece_centree(self.white_knight, (r, c))

                if board[r][c] == 'wB':
                    self.dessin_piece_centree(self.white_bishop, (r, c), -13)

                if board[r][c] == 'wQ':
                    self.dessin_piece_centree(self.white_queen, (r, c))

                if board[r][c] == 'wK':
                    self.dessin_piece_centree(self.white_king, (r, c), -18)

    def EndGame(self, board):
        self.PrintMessage("Press any key to exit.")
        self.do_paint(board)  # draw board to show end game status
        # TODO remove this flip
        kengi.flip()

        pygame.event.set_blocked(pygame.MOUSEMOTION)
        while 1:
            e = pygame.event.wait()
            if e.type == pygame.KEYDOWN:
                pygame.quit()
                sys.exit(0)
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

    def GetPlayerInput(self, board, currentColor) -> tuple:
        """
        format returned: (from_row,from_col), (to_row,to_col)
        """
        fromSquareChosen = 0
        toSquareChosen = 0
        while not fromSquareChosen or not toSquareChosen:
            squareClicked = []
            pygame.event.set_blocked(pygame.MOUSEMOTION)
            e = pygame.event.wait()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    fromSquareChosen = 0
                    fromTuple = []
            if e.type == pygame.MOUSEBUTTONDOWN:
                (mouseX, mouseY) = pygame.mouse.get_pos()
                print(mouseX, mouseY)
                squareClicked = self.ConvertToChessCoords((mouseX, mouseY))
                if squareClicked[0] < 0 or squareClicked[0] > 7 or squareClicked[1] < 0 or squareClicked[1] > 7:
                    squareClicked = []  # not a valid chess square
            if e.type == pygame.QUIT:  # the "x" kill button
                pygame.quit()
                sys.exit(0)

            if not fromSquareChosen and not toSquareChosen:
                self.do_paint(board)
                if len(squareClicked) != 0:
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
                possibleDestinations = self.Rules.GetListOfValidMoves(board, currentColor, fromTuple)

                # TODO remove the extra flip!!
                self.do_paint(board, possibleDestinations)
                kengi.flip()

                if squareClicked != []:
                    (r, c) = squareClicked
                    if squareClicked in possibleDestinations:
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

        return fromTuple, toTuple

    def GetClickedSquare(self, mouseX, mouseY):
        # test function
        print("User clicked screen position x =", mouseX, "y =", mouseY)
        (row, col) = self.ConvertToChessCoords((mouseX, mouseY))
        if col < 8 and col >= 0 and row < 8 and row >= 0:
            print("  Chess board units row =", row, "col =", col)

    # def TestRoutine(self):
    #     # test function
    #     pygame.event.set_blocked(MOUSEMOTION)
    #     while 1:
    #         e = pygame.event.wait()
    #         if e.type is QUIT:
    #             return
    #         if e.type is KEYDOWN:
    #             if e.key is K_ESCAPE:
    #                 pygame.quit()
    #                 return
    #         if e.type is MOUSEBUTTONDOWN:
    #             (mouseX, mouseY) = pygame.mouse.get_pos()
    #             # x is horizontal, y is vertical
    #             # (x=0,y=0) is upper-left corner of the screen
    #             self.GetClickedSquare(mouseX, mouseY)

    def dessin_piece_centree(self, black_pawn, case, voffset=-10):
        (screenX, screenY) = self.ConvertToScreenCoords(case)
        # on souhaite que le centre de la case & le centre de l'image coincident
        # Pour cela, on calcule le coin en haut à gauche qui va bien...
        delta = self.square_size // 2
        centre_case = (screenX + delta, screenY + delta)
        tmp = black_pawn.get_size()
        goodx = centre_case[0] - tmp[0] // 2
        goody = centre_case[1] - tmp[1] // 2
        goody += voffset
        self.screen.blit(black_pawn, (goodx, goody))


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
