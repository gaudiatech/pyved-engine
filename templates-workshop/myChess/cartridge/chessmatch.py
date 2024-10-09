from . import chdefs
from .chdefs import BOARD_POS

from .main_gui_view import PopupPromotion
from .model import *
from .ChessmatchMod import ChessgameMod

from . import pimodules

# --- alias
pyv = pimodules.pyved_engine
pygame = pyv.pygame

# --- constants
PAUSE_SEC = 3
W_SIZE = (850, 500)


class ChessGameView(pyv.Emitter):  # (pyv.EvListener):
    BG_COLOR = (125, 110, 120)

    def __init__(self, boardref):
        super().__init__()

        self.Rules = ChessRules()
        self.board = boardref  # update from outside

        self._fluo_squares = None  # qd qq chose est select ->affiche ou on peut bouger
        self.possibleDestinations = None

        # gui
        self.fromSquareChosen = self.toSquareChosen = None
        self._sortie_subloop = self._sortie_subloop2 = None

        # self.textBox = ScrollingTextBox(self.screen, 525, 825, 50, 450)
        # -* Hacking begins *-
        self.textBox = pyv.console.CustomConsole(pyv.get_surface(), (BOARD_POS[0], 4, 640, 133))
        self.textBox.active = True
        self.textBox.bg_color = self.BG_COLOR  # customize console
        self.textBox.font_size = 25
        # self.textBox.Add = extAdd
        self.textBox.Add = self.textBox.output
        # -* Hacking done *-

        # <link to assets>
        for assetname, val in pyv.vars.images.items():
            setattr(self, assetname, val)
        self.square_size = 50

        self.fontDefault = pygame.font.Font(None, 20)
        self.ready_to_quit = False

    def PrintMessage(self, message):
        # prints a string to the area to the right of the board
        # print('envoi [{}] ds la console...'.format(message))
        self.textBox.Add(message)
        # self.textBox.draw()

    def ConvertToScreenCoords(self, chessSquareTuple):
        # converts a (row,col) chessSquare into the pixel location of the upper-left corner of the square
        (row, col) = chessSquareTuple
        screenX = BOARD_POS[0] + col * self.square_size
        screenY = BOARD_POS[1] + row * self.square_size
        return screenX, screenY

    def ConvertToChessCoords(self, screenPositionTuple):
        # converts a screen pixel location (X,Y) into a chessSquare tuple (row,col)
        # x is horizontal, y is vertical
        # (x=0,y=0) is upper-left corner of the screen
        (X, Y) = screenPositionTuple
        row = (Y - BOARD_POS[1]) / self.square_size
        col = (X - BOARD_POS[0]) / self.square_size
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
        color = (255, 255, 255)  # white
        antialias = 1

        # top and bottom - display cols
        for c in range(boardSize):
            for r in [-1, boardSize]:
                (screenX, screenY) = self.ConvertToScreenCoords((r, c))
                screenX = screenX + self.square_size / 2
                screenY = screenY + self.square_size / 2
                notation = to_algebraic_notation_col(c)
                renderedLine = self.fontDefault.render(notation, antialias, color)
                scrsurf.blit(renderedLine, (screenX, screenY))

        # left and right - display rows
        for r in range(boardSize):
            for c in [-1, boardSize]:
                (screenX, screenY) = self.ConvertToScreenCoords((r, c))
                screenX = screenX + self.square_size / 2
                screenY = screenY + self.square_size / 2
                notation = to_algebraic_notation_row(r)
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
                if board[r][c] == 'b'+C_PAWN:
                    self.dessin_piece_centree(scrsurf, self.black_pawn, (r, c))

                if board[r][c] == 'b'+C_ROOK:
                    self.dessin_piece_centree(scrsurf, self.black_rook, (r, c))

                if board[r][c] == 'b'+C_KNIGHT:
                    self.dessin_piece_centree(scrsurf, self.black_knight, (r, c))

                if board[r][c] == 'b'+C_BISHOP:
                    self.dessin_piece_centree(scrsurf, self.black_bishop, (r, c), -13)

                if board[r][c] == 'b'+C_QUEEN:
                    self.dessin_piece_centree(scrsurf, self.black_queen, (r, c))

                if board[r][c] == 'b'+C_KING:
                    self.dessin_piece_centree(scrsurf, self.black_king, (r, c), -18)

                if board[r][c] == 'w'+C_PAWN:
                    self.dessin_piece_centree(scrsurf, self.white_pawn, (r, c))

                if board[r][c] == 'w'+C_ROOK:
                    self.dessin_piece_centree(scrsurf, self.white_rook, (r, c))

                if board[r][c] == 'w'+C_KNIGHT:
                    self.dessin_piece_centree(scrsurf, self.white_knight, (r, c))

                if board[r][c] == 'w'+C_BISHOP:
                    self.dessin_piece_centree(scrsurf, self.white_bishop, (r, c), -13)

                if board[r][c] == 'w'+C_QUEEN:
                    self.dessin_piece_centree(scrsurf, self.white_queen, (r, c))

                if board[r][c] == 'w'+C_KING:
                    self.dessin_piece_centree(scrsurf, self.white_king, (r, c), -18)

    def EndGame(self, board):
        if not self.ready_to_quit:
            self.PrintMessage("Press any key to exit.")
            self.ready_to_quit = True

        self.drawboard(pyv.get_surface(), board)  # draw board to show end game status
        # TODO remove this flip
        # pyv.flip()

    def forward_mouseev(self, ev):
        """
        format save to self._sortie_subloop:
        (from_row,from_col), (to_row,to_col)
        """

        board = self.board
        curr_chesscolor = self.board.curr_player

        (mouseX, mouseY) = ev.pos
        squareClicked = self.ConvertToChessCoords((mouseX, mouseY))
        if (not (0 <= squareClicked[0] <= 7)) or (not(0 <= squareClicked[1] <= 7)):  # TODO internaliser ds convert..
            # set all None, bc its not a valid chess square
            self._fluo_squares = None
            self.possibleDestinations = None
            self.fromSquareChosen = None
            return

        if not self.fromSquareChosen:
            r, c = squareClicked
            validselection = (curr_chesscolor == C_BLACK_PLAYER and 'b' == board.state[r][c][0])
            validselection = validselection or (curr_chesscolor == C_WHITE_PLAYER and 'w' == board.state[r][c][0])
            if validselection:
                self.fromSquareChosen = squareClicked
                fromTuple = tuple(squareClicked)
                # TODO set fromTuple properly
                self.possibleDestinations = self.Rules.get_valid_moves(board, curr_chesscolor, fromTuple)
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


class ChessTicker(pyv.EvListener):
    def __init__(self, refmod, refview):
        super().__init__()

        self.model = refmod
        self.refview = refview
        self.refview.board = refmod.get_board()
        self.stored_human_input = None  # when smth has been played!

        # self._curr_pl_idx = 0

        # +1 when both have played!!
        self._turn_count = refmod.get_turn()//2

        self.endgame_msg_added = False

        # self.board_st = refmod.board.state
        self.ready_to_quit = False
        self.endgame_msg_added = False

    def on_checkmate(self, ev):
        self.ready_to_quit = True

    def on_check(self, ev):
        players = self.model.players
        pl_color = self.model.get_board().curr_player
        curr_pl_idx = ['white', 'black'].index(pl_color)

        curr_pp = players[curr_pl_idx]
        suffx = '{} ({}) is in check'.format(curr_pp.name, curr_pp.color)
        self.refview.PrintMessage("Warning! " + suffx)

    def on_move_chosen(self, ev):  # as defined in ChessEvents
        self.stored_human_input = [ev.from_cell, ev.to_cell]
        # print('-- STORING - -', self.stored_human_input)

    def on_keydown(self, ev):
        if ev.key == pyv.pygame.K_ESCAPE:
            self.pev(pyv.EngineEvTypes.Gameover)
        elif ev.key == pyv.pygame.K_SPACE:
            print(self.model.get_board().serialize())
        elif ev.key == pyv.pygame.K_BACKSPACE:
            self.model.get_board().undo_move()
        elif self.ready_to_quit:
            self.pev(pyv.EngineEvTypes.StatePop)

    def on_mousedown(self, ev):
        self.refview.forward_mouseev(ev)

    def on_gameover(self, ev):
        """
        maybe there are other ways to exit than just pressing ESC...
        in this method, we update the game object
        """
        pyv.vars.gameover = True

    def on_quit(self, ev):  # press quit button
        self.on_gameover(ev)

    def on_paint(self, ev):
        self.refview.drawboard(ev.screen, self.model.get_board().state)

    def on_update(self, ev):
        # board_st = self.board_st
        players = self.model.players
        pl_color = self.model.get_curr_player()
        # print('color thats now playing is: ', pl_color)
        curr_pl_idx = ['white', 'black'].index(pl_color)
        curr_player = players[curr_pl_idx]

        if self.ready_to_quit:
            # --- manage end game ---
            if not self.endgame_msg_added:
                self.endgame_msg_added = True
                self.refview.PrintMessage("CHECKMATE!")
                winnerIndex = (curr_pl_idx+1) % 2
                self.refview.PrintMessage(
                    players[winnerIndex].name + " (" + players[winnerIndex].color + ") won the game!")

                self.refview.EndGame(self.model.get_board_state())
            return

        # -- the problem with THAT type of code is that it BLOCKS the soft!
        # if player[currentPlayerIndex].type == 'AI':
        #     moveTuple = player[currentPlayerIndex].GetMove(board.GetState(), currentColor)
        # else:
        #     moveTuple = Gui.GetPlayerInput(board_st, currentColor)
        # TODO repair human vs A.I. play

        move_report = None
        refboard = self.model.get_board()

        if curr_player.type == 'human':
            moveTuple = self.stored_human_input
            if moveTuple:
                move_report = self.model.play(moveTuple)
                # moveReport = string like "White Bishop moves from A1 to C3" (+) "and captures ___!"
                self.stored_human_input = None
        else:
            tmp_ai_move = curr_player.GetMove(refboard, curr_player.color)
            move_report = self.model.play(tmp_ai_move)

        if move_report:  # smth has been played!
            self.refview.PrintMessage(move_report)
            # this will cause the currentPlayerIndex to toggle between 1 and 0

            # -- iterate game --
            #self._curr_pl_idx = (self._curr_pl_idx + 1) % 2
            #curr_player = players[self._curr_pl_idx]
            # self.refview.curr_color =  ['white', 'black'][self._curr_pl_idx]

            # TODO repair feat.
            # if AIvsAI and AIpause:
            #     time.sleep(AIpauseSeconds)

            #currentColor = curr_player.color
            currentColor = self.model.get_curr_player()

            # hardcoded so that player 1 is always white
            if currentColor == 'white':
                self._turn_count = self._turn_count + 1
            self.refview.PrintMessage("")
            baseMsg = "TURN %s - %s (%s)" % (str(self._turn_count), curr_player.name, currentColor)
            self.refview.PrintMessage("--%s--" % baseMsg)


class ChessmatchState(pyv.BaseGameState):
    # bind state_id to class is done automatically by kengi (part 1 /2)

    def enter(self):
        self.m = ChessgameMod()

        # TODO make the view active
        pygamegui = self.v = ChessGameView(self.m.get_board())

        self.t = ChessTicker(self.m, pygamegui)  # ?? kind like a controller
        self.t.turn_on()

        self.addon = PopupPromotion(self.m)
        self.addon.turn_on()

    def release(self):
        self.addon.turn_off()
        self.t.turn_off()


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
