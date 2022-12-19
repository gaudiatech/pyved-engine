"""
Project - Python Chess
(c) All rights reserved | Code LICENCE = GNU GPL

This is a joint work. Authors are:

- Steve Osborne (the very first prototype, encoding game rules)
   [contact: srosborne_at_gmail.com]

- Thomas Iwaszko (port to python3+kengi, game improvement)
   [contact: tom@kata.games]
"""
import time

import katagames_engine as kengi
from ChessBoard import ChessBoard
from ChessGUI_pygame import ChessGameView
from ChessRules import ChessRules
from chess.chess_defs import ChessEvents
from players import ChessPlayer, ChessAI_random, ChessAI_defense, ChessAI_offense


# 0 for normal board setup;
# see ChessBoard class for other options (for testing purposes)
# e.g. the debug mode can use arg 2 instead of 0
board = ChessBoard(0)

rules = ChessRules()
player = None
AIvsAI = False
AIpause = False
AIpauseSeconds = 0.0
endgame_msg_added = False

# constants:
PAUSE_SEC = 3


def initchess():
    global player, AIpause, AIvsAI, AIpauseSeconds, endgame_msg_added, PAUSE_SEC
    # gameSetupParams: Player 1 and 2 Name, Color, Human/AI level
    # if self.debugMode:
    # 	player1Name = 'Kasparov'
    # 	player1Type = 'human'
    # 	player1Color = 'white'
    # 	player2Name = 'Light Blue'
    # 	player2Type = 'randomAI'
    # 	player2Color = 'black'

    default_config = (
        'Player1', 'white', 'human',
        'AI', 'black', 'defenseAI'
    )
    (player1Name, player1Color, player1Type, player2Name, player2Color, player2Type) = default_config

    player = [0, 0]
    if player1Type == 'human':
        player[0] = ChessPlayer(player1Name, player1Color)
    elif player1Type == 'randomAI':
        player[0] = ChessAI_random(player1Name, player1Color)
    elif player1Type == 'defenseAI':
        player[0] = ChessAI_defense(player1Name, player1Color)
    elif player1Type == 'offenseAI':
        player[0] = ChessAI_offense(player1Name, player1Color)

    if player2Type == 'human':
        player[1] = ChessPlayer(player2Name, player2Color)
    elif player2Type == 'randomAI':
        player[1] = ChessAI_random(player2Name, player2Color)
    elif player2Type == 'defenseAI':
        player[1] = ChessAI_defense(player2Name, player2Color)
    elif player2Type == 'offenseAI':
        player[1] = ChessAI_offense(player2Name, player2Color)

    if 'AI' in player[0].type and 'AI' in player[1].type:
        AIvsAI = True
    else:
        AIvsAI = False
    if PAUSE_SEC > 0:
        AIpause = True
        AIpauseSeconds = int(PAUSE_SEC)
    else:
        AIpause = False


class ChessTicker(kengi.EvListener):
    def __init__(self, refview):
        global board
        super().__init__()
        self.refview = refview
        self.refview.board = board
        self.storedinput = None  # when smth has been played!
        self._curr_pl_idx = 0
        self._turn_count = 0
        self.endgame_msg_added = False
        self.board_st = board.GetState()
        self.ready_to_quit = False
        self.endgame_msg_added = False

    def on_move_chosen(self, ev):  # as defined in ChessEvents
        self.storedinput = [ev.from_cell, ev.to_cell]
        print('-- STORING - -', self.storedinput)

    def on_keydown(self, ev):
        if ev.key == kengi.pygame.K_ESCAPE:
            self.pev(kengi.EngineEvTypes.Gameover)

    def on_mousedown(self, ev):
        self.refview.forward_mouseev(ev)

    def on_gameover(self, ev):
        """
        maybe there are other ways to exit than just pressing ESC...
        in this method, we update the game object
        """
        global game_obj
        print('gameover capté par ticker!')
        game_obj.gameover = True

    def on_paint(self, ev):
        self.refview.drawboard(ev.screen, self.board_st)

    def on_update(self, ev):
        global board
        board_st = board.GetState()

        if not self.ready_to_quit:

            # -- the problem with THAT type of code is that it BLOCKS the soft!
            # if player[currentPlayerIndex].type == 'AI':
            #     moveTuple = player[currentPlayerIndex].GetMove(board.GetState(), currentColor)
            # else:
            #     moveTuple = Gui.GetPlayerInput(board_st, currentColor)

            # TODO repair human vs A.I. play

            moveTuple = self.storedinput
            if moveTuple:
                moveReport = board.move_piece(moveTuple)
                # moveReport = string like "White Bishop moves from A1 to C3" (+) "and captures ___!"
                self.refview.PrintMessage(moveReport)

                # this will cause the currentPlayerIndex to toggle between 1 and 0
                self._curr_pl_idx = (self._curr_pl_idx + 1) % 2
                self.refview.curr_color = ['white', 'black'][self._curr_pl_idx]
                if AIvsAI and AIpause:
                    time.sleep(AIpauseSeconds)
                if rules.IsCheckmate(board.GetState(), player[self._curr_pl_idx].color):
                    self.ready_to_quit = True

                # ----
                # - iterate game -
                currentColor = player[self._curr_pl_idx].color
                # hardcoded so that player 1 is always white
                if currentColor == 'white':
                    self._turn_count = self._turn_count + 1
                self.refview.PrintMessage("")
                baseMsg = "TURN %s - %s (%s)" % (str(self._turn_count), player[self._curr_pl_idx].name, currentColor)
                self.refview.PrintMessage("--%s--" % baseMsg)

                if rules.IsInCheck(board_st, currentColor):
                    pobj = player[self._curr_pl_idx]
                    suffx = '{} ({}) is in check'.format(pobj.name, pobj.color)
                    self.refview.PrintMessage("Warning..." + suffx)

                self.storedinput = None

        else:
            # --- end game ---
            if not self.endgame_msg_added:
                self.refview.PrintMessage("CHECKMATE!")
                winnerIndex = (self._curr_pl_idx + 1) % 2
                self.refview.PrintMessage(
                    player[winnerIndex].name + " (" + player[winnerIndex].color + ") won the game!")
                self.endgame_msg_added = True
                self.refview.EndGame(self.board_st)

        # self.refview.drawboard(gl_screen_ref, board_st)


# parser = OptionParser()
# parser.add_option(
#     "-d", dest="debug",
#     action="store_true", default=False, help="Enable debug mode (different starting board configuration)"
# )
# parser.add_option(
#     "-t", dest="text",
#     action="store_true", default=False, help="Use text-based GUI"
# )
# parser.add_option(
#     "-o", dest="old",
#     action="store_true", default=False, help="Use old graphics in pygame GUI"
# )
# parser.add_option(
#     "-p", dest="pauseSeconds", metavar="SECONDS",
#     action="store", default=0, help="Sets time to pause between moves in AI vs. AI games (default = 0)"
# )
# (giv_options, args) = parser.parse_args()

class MyChessGame(kengi.GameTpl):

    def enter(self, vms=None):
        global evmanager, gl_screen_ref
        kengi.init(1)
        evmanager = kengi.get_ev_manager()
        evmanager.setup(ChessEvents)
        self._manager = evmanager
        initchess()
        gl_screen_ref = kengi.get_surface()

        pygamegui = ChessGameView(gl_screen_ref)

        ticker = ChessTicker(pygamegui)
        ticker.turn_on()


game_obj = MyChessGame()
game_obj.loop()
