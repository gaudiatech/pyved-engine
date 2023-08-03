import chdefs
from ai_players import ChessAI_random, ChessAI_defense, ChessAI_offense
from model import ChessRules, ChessBoard, ChessPlayer, BOARDS_DEBUG


class ChessgameMod:
    def __init__(self):

        # 0 for normal board setup; see ChessBoard class for other options (testing purposes)
        # e.g. the debug mode can use arg 2 instead of 0

        # self.board = ChessBoard(serial=BOARDS_DEBUG['e.p.'])

        self._board = ChessBoard(0)
        self.rules = ChessRules()
        self.players = None
        self._initplayers()

    def play(self, move_tuple):
        self._board.move_piece(move_tuple)

    def get_turn(self):
        return self._board.turn

    def get_curr_player(self):
        return self._board.curr_player

    def get_board(self):
        return self._board

    def get_board_state(self):
        return self._board.state

    def _initplayers(self):
        default_config = (
            'AI', 'white', 'randomAI',
            'AI', 'black', 'randomAI'
        )
        (player1Name, player1Color, player1Type, player2Name, player2Color, player2Type) = default_config
        # replace default config playertypes by what has been stored in chdefs
        player1Type, player2Type = chdefs.pltype1, chdefs.pltype2
        if player2Type == 'human':
            player2Name = 'Player2'
        if player1Type == 'human':
            player1Name = 'Player1'

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

        # - disabled feature: pause when its a AI vs AI match
        # if 'AI' in self.players[0].type and 'AI' in self.players[1].type:
        #     AIvsAI = True
        # else:
        #     AIvsAI = False
        # if PAUSE_SEC > 0:
        #     AIpause = True
        #     AIpauseSeconds = int(PAUSE_SEC)
        # else:
        #     AIpause = False
