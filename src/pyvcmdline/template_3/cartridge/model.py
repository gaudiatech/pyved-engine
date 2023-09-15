"""
model for the game of chess (whats a chess Player/a chess Board +what are the rules?)
"""
from .chess_rules import *
from . import chdefs
from .chdefs import ChessEvents
from . import pimodules


pyv = pimodules.pyved_engine
# todo future model will use a class for chesspiece + an int matrix
# i should be able to write high-level ideas such as:
# if board['d4'].is_pawn():
#     ...

# -------------------------------------
#  projekt below!
# -------------------------------------
# class ChessPiece:
#     KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN = 'king', 'queen', 'rook', 'bishop', 'knight', 'pawn'
#     TYPES = (KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN)
#
#     free_id = 2048  # abritrary
#
#     # warning! That trick wont work if you change chesspiece codes. Now Im using str values
#     def __getattr__(self, attr_name):
#         if attr_name[0:3] == 'is_':
#             x = attr_name[3:]
#             if x == 'white':
#                 return lambda: self.color == C_WHITE_PLAYER
#             elif x == 'black':
#                 return lambda: self.color == C_BLACK_PLAYER
#             else:
#                 for cp_type in self.TYPES:
#                     if x == cp_type:
#                         return lambda: self.cp_type == x
#         raise AttributeError('')
#
#     def __init__(self, color, cp_type, curr_square=None):
#         self.p_id = self.__class__.free_id
#         self.__class__.free_id -= 1
#         self.color = color
#         if color not in (C_BLACK_PLAYER, C_WHITE_PLAYER):
#             raise ValueError('ERR: looks like the "color" arg. passed isnt valid:', color)
#         self.cp_type = cp_type
#         self.loc = curr_square
#         if curr_square:
#             if not (0 <= curr_square[0] < 8 and 0 <= curr_square[1] < 8):
#                 raise ValueError('ERR: looks like the curr_square arg. passed isnt valid:', curr_square)
#
#
# tt = ChessPiece('black', 'king')
# print(tt.is_black())
# print(tt.is_white())
# print('-')
# print(tt.is_pawn())
# print(tt.is_bishop())
# print(tt.is_king())


__all__ = [
    'C_KING', 'C_QUEEN', 'C_ROOK', 'C_BISHOP', 'C_KNIGHT', 'C_PAWN',
    'C_BLACK_PLAYER', 'C_WHITE_PLAYER',
    'C_EMPTY_SQUARE',

    'ChessPlayer',
    'ChessBoard',
    'ChessRules',

    'to_algebraic_notation_col',
    'to_algebraic_notation_row'
]


def colorsym(x):
    if x == C_BLACK_PLAYER:
        adhoc_sym = 'b'
    elif x == C_WHITE_PLAYER:
        adhoc_sym = 'w'
    else:
        raise ValueError('non-valid chesscolor:', x)
    return adhoc_sym


class ChessPlayer:
    @classmethod
    def conv_move(cls, packedcoords):
        """
        utility method so i can input moves such as 'e2e4' instead of ((4,1),(4,3))
        which is very un-natural
        """
        if len(packedcoords) != 4:
            raise ValueError('arg passed to ChessAI.conv_move has not the expected format! Received:', packedcoords)
        li_given_char = list(packedcoords)
        ref = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        t1 = [8 - int(li_given_char[1]), ref.index(li_given_char[0])]
        t2 = [8 - int(li_given_char[3]), ref.index(li_given_char[2])]
        return tuple(t1), tuple(t2)

    def __init__(self, name, color: str):
        self._name = name
        if color not in (C_BLACK_PLAYER, C_WHITE_PLAYER):
            raise ValueError('invalid player color passed!')
        self._color = color
        self._type = 'human'

    @property
    def name(self):
        return self._name

    @property
    def color(self):
        return self._color

    @property
    def type(self):
        return self._type


class ChessBoard(pyv.Emitter):
    """
    Board layout; contains what pieces are present at each square
    """
    EMPTY_SYM = 'ee'

    def serialize(self):
        serial = ''
        for j in range(8):
            for i in range(8):
                serial += self.squares[j][i]
        serial += str(self._play_sequence)
        return serial

    def square_has(self, sq, chesspiece, chesscolor=None):
        content = self.squares[sq[0]][sq[1]]
        if chesscolor is None:
            return chesspiece in content
        else:
            adhoc_sym = colorsym(chesscolor)
            return content == adhoc_sym + chesspiece

    def square_ctrled_by(self, sq, chesscolor):
        """
        return True if the square has a piece that belongs to player identified by 'chesscolor'
        :param sq:
        :param chesscolor:
        :return:
        """
        adhoc_sym = colorsym(chesscolor)
        content = self.squares[sq[0]][sq[1]]
        return adhoc_sym in content

    @property
    def curr_player(self):
        if not self._play_sequence % 2:
            return C_WHITE_PLAYER
        else:
            return C_BLACK_PLAYER

    def _load_serial(self, s):
        elements = [s[i:i + 2] for i in range(0, 8 * 8 * 2, 2)]
        self._play_sequence = int(s[8 * 8 * 2:])
        for rank, elt in enumerate(elements):
            i, j = rank // 8, rank % 8
            self.squares[i][j] = elt

    def __init__(self, setup_type=0, serial=None):
        super().__init__()
        # keep all informations about the last move, so we can undo it
        self._backup_serial = None

        self._prev_source_square = None
        self._prev_target_square = None
        self._prev_source_piece = None
        self._prev_target_piece = None
        self._prev_player = None

        # infos to keep, in order to detect when its possible to capture "en passant"
        self.pawn_jumped = False
        self.jumping_pawn_loc = None
        self.jumped_over = None

        # infos: has the kind moved? rooks moved? (pour le roque)
        self.bR1_moved = self.bR8_moved = False
        self.wR1_moved = self.wR8_moved = False
        self.bK_moved = False
        self.wK_moved = False

        self._play_sequence = 0
        self.squares = list()
        for _ in range(8):
            row = [self.EMPTY_SYM] * 8
            self.squares.append(row)

        # ------------------
        #  init board. based on the serial
        # ------------------
        if serial is not None:
            self._load_serial(serial)
            return

        # ------------------
        #  init board. based on the setup_type code
        # ------------------
        if setup_type == 0:
            self.squares[0] = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR']
            self.squares[1] = ['b_'] * 8

            self.squares[6] = ['w_'] * 8
            self.squares[7] = ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']

        # Debugging set-ups
        # Testing IsLegalMove
        elif setup_type == 1:
            self.squares[0] = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR']
            self.squares[6] = ['w_'] * 8
            self.squares[7] = ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']

        # Testing IsInCheck, Checkmate
        elif setup_type == 2:
            self.squares[2][4] = 'bK'
            self.squares[3][4] = 'bR'
            self.squares[4][2] = 'bB'
            self.squares[4][6] = 'wR'
            self.squares[6][0] = 'wB'
            self.squares[7] = [C_EMPTY_SQUARE, C_EMPTY_SQUARE, C_EMPTY_SQUARE, 'wK', 'wQ', C_EMPTY_SQUARE, 'wN',
                               C_EMPTY_SQUARE]

        # Testing Defensive AI
        elif setup_type == 3:
            self.squares[2][4] = 'bK'
            self.squares[3][4] = 'bR'
            self.squares[4][2] = 'bB'
            self.squares[4][6] = 'wR'
            self.squares[7] = [C_EMPTY_SQUARE, C_EMPTY_SQUARE, C_EMPTY_SQUARE, 'wK', 'wQ', C_EMPTY_SQUARE, 'wN',
                               C_EMPTY_SQUARE]

        print(self.serialize())

    def get_piece_positions(self, color_identifier, piece_t):
        """
        returns list of piece positions; will be empty if color piece doesn't exist on board
        """
        myPieceType = {
            'king': 'K',
            'queen': 'Q',
            'rook': 'R',
            'knight': 'N',
            'bishop': 'B',
            'pawn': 'P'
        }[piece_t]

        if color_identifier not in (C_BLACK_PLAYER, C_WHITE_PLAYER):
            raise ValueError('color non-valid')
        color_tag = 'w' if (color_identifier == C_WHITE_PLAYER) else 'b'

        piecePositions = list()
        for row in range(8):
            for col in range(8):
                piece = self.squares[row][col]
                if myPieceType in piece:
                    if color_tag in piece:
                        piecePositions.append((row, col))
        return piecePositions

    @property
    def turn(self):
        return self._play_sequence

    @property
    def state(self):
        return self.squares

    def ConvertMoveTupleListToAlgebraicNotation(self, moveTupleList):
        newTupleList = []
        for move in moveTupleList:
            newTupleList.append((self.ConvertToAlgebraicNotation(move[0]), self.ConvertToAlgebraicNotation(move[1])))
        return newTupleList

    def ConvertSquareListToAlgebraicNotation(self, list):
        newList = []
        for square in list:
            newList.append(self.ConvertToAlgebraicNotation(square))
        return newList

    def GetFullString(self, p):
        if 'b' in p:
            name = "black "
        else:
            name = "white "

        if C_PAWN in p:
            name = name + "pawn"
        if C_ROOK in p:
            name = name + "rook"
        if C_KNIGHT in p:
            name = name + "knight"
        if C_BISHOP in p:
            name = name + "bishop"
        if C_QUEEN in p:
            name = name + "queen"
        if C_KING in p:
            name = name + "king"

        return name

    @property
    def prev_player(self):
        return self._prev_player

    def do_castle(self, chesscolor, queen_side=False):
        sym = colorsym(chesscolor)
        if chesscolor == C_BLACK_PLAYER:
            self.bK_moved = True
            if queen_side:
                self.bR1_moved = True
            else:
                self.bR8_moved = True
            message_str = 'Black castles ' + ('(queen-side)' if queen_side else '(king-side)')
            j = 0
        elif chesscolor == C_WHITE_PLAYER:
            self.wK_moved = True
            if queen_side:
                self.wR1_moved = True
            else:
                self.wR8_moved = True
            message_str = 'White castles ' + ('(queen-side)' if queen_side else '(king-side)')
            j = 7
        else:
            raise ValueError('non-valid chess arg:', chesscolor)

        # move the king
        self.squares[j][4] = C_EMPTY_SQUARE
        if queen_side:
            self.squares[j][2] = sym + C_KING
        else:
            self.squares[j][6] = sym + C_KING

        # move the rook
        if queen_side:
            self.squares[j][0] = C_EMPTY_SQUARE
            self.squares[j][3] = sym + C_ROOK
        else:
            self.squares[j][7] = C_EMPTY_SQUARE
            self.squares[j][5] = sym + C_ROOK

        # turn is over
        self._play_sequence += 1
        return message_str

    def promote(self, sq, wanted_piece):
        """
        called when the HUMAN player has selected the wanted piece... We simply replace
        :param sq:
        :param wanted_piece:
        :return:
        """
        short = {
            'queen': 'Q',
            'rook': 'R',
            'knight': 'N',
            'bishop': 'B'
        }[wanted_piece]
        newdata = colorsym(self.curr_player)+short
        self.squares[sq[0]][sq[1]] = newdata
        self.finish_promotion(wanted_piece)

    def _popup_promo(self):
        self.paused = True
        self.pev(ChessEvents.PromotionPopup, target_square=self._prev_target_square, plcolor=self.curr_player)

    def move_piece(self, mv_tuple):
        """
        :param mv_tuple: can be something like ([1,1], [2,6])
        changes the state of the board
        """
        fromSquare_r, fromSquare_c = self._prev_source_square = mv_tuple[0]
        toSquare_r, toSquare_c = self._prev_target_square = mv_tuple[1]

        self._prev_player = self.curr_player
        self._prev_source_piece = self.squares[fromSquare_r][fromSquare_c]
        self._prev_target_piece = self.squares[toSquare_r][toSquare_c]

        fromPiece_fullString = self.GetFullString(self._prev_source_piece)
        toPiece_fullString = self.GetFullString(self._prev_target_piece)
        self._backup_serial = self.serialize()

        # detect castling:
        if self._prev_source_piece in ('bK', 'wK'):
            if fromSquare_r == toSquare_r == 7 and fromSquare_c == 4 and toSquare_c == 6:  # small castle white
                return self.do_castle(self.curr_player)
            if fromSquare_r == toSquare_r == 7 and fromSquare_c == 4 and toSquare_c == 2:  # large castle white
                return self.do_castle(self.curr_player, True)
            if fromSquare_r == toSquare_r == 0 and fromSquare_c == 4 and toSquare_c == 6:  # small castle black
                return self.do_castle(self.curr_player)
            if fromSquare_r == toSquare_r == 0 and fromSquare_c == 4 and toSquare_c == 2:  # large castle white
                return self.do_castle(self.curr_player, True)

        if self._prev_source_piece == 'wR':
            if self._prev_source_square[0] == 7 and self._prev_source_square[1] == 7:
                self.wR8_moved = True
            elif self._prev_source_square[0] == 7 and self._prev_source_square[1] == 0:
                self.wR1_moved = True
        if self._prev_source_piece == 'bR':
            if self._prev_source_square[0] == 0 and self._prev_source_square[1] == 7:
                self.bR8_moved = True
            elif self._prev_source_square[0] == 0 and self._prev_source_square[1] == 0:
                self.bR1_moved = True
        elif self._prev_source_piece == 'bK':
            self.bK_moved = True
        elif self._prev_source_piece == 'wK':
            self.wK_moved = True

        en_passant = False
        messageString = 'ERR.'

        if self.pawn_jumped:
            if toSquare_r == self.jumped_over[0] and toSquare_c == self.jumped_over[1]:
                en_passant = True

                a, b = self.jumping_pawn_loc
                self.squares[fromSquare_r][fromSquare_c] = C_EMPTY_SQUARE  # square we leave
                self.squares[a][b] = C_EMPTY_SQUARE  # capture the pawn that jumped
                jo_r, jo_c = self.jumped_over
                self.squares[jo_r][jo_c] = self._prev_source_piece  # occupy new location
                self._play_sequence += 1

                messageString = fromPiece_fullString + " from " + coords_to_alg(mv_tuple[0]) + \
                                " captures " + toPiece_fullString + " at " + coords_to_alg(
                    self.jumping_pawn_loc) + " (en passant)"
                messageString.capitalize()

        # reset bc its not possible to take when its more than 1 turn
        # reset
        self.pawn_jumped = False
        self.jumping_pawn_loc = None
        self.jumped_over = None
        if en_passant:
            return messageString

        self.squares[fromSquare_r][fromSquare_c] = C_EMPTY_SQUARE  # square left
        self.squares[toSquare_r][toSquare_c] = self._prev_source_piece  # square newly taken

        if C_EMPTY_SQUARE == self._prev_target_piece:
            capture = False
            messageString = fromPiece_fullString + " moves from " + coords_to_alg(mv_tuple[0]) + \
                            " to " + coords_to_alg(mv_tuple[1])
        else:
            capture = True
            messageString = fromPiece_fullString + " from " + coords_to_alg(mv_tuple[0]) + \
                            " captures " + toPiece_fullString + " at " + coords_to_alg(
                mv_tuple[1]) + "!"
        messageString.capitalize()

        if self._prev_source_piece == 'w'+C_PAWN:
            if toSquare_r == 0:
                # auto-promote to queen
                # self.squares[fromSquare_r][fromSquare_c] = C_EMPTY_SQUARE  # square left
                # self.squares[toSquare_r][toSquare_c] = colorsym(self.curr_player)+'Q'
                # self._play_sequence += 1
                # return "White pawn moves from " + coords_to_alg(mv_tuple[0]) + \
                #             " to " + coords_to_alg(mv_tuple[1]) + ", gets promoted"
                self._popup_promo()
                return messageString
        if self._prev_source_piece == 'b'+C_PAWN:
            if toSquare_r == 7:
                # auto-promote to queen
                # self.squares[fromSquare_r][fromSquare_c] = C_EMPTY_SQUARE  # square left
                # self.squares[toSquare_r][toSquare_c] = colorsym(self.curr_player)+'Q'
                # self._play_sequence += 1
                # return "Black pawn moves from " + coords_to_alg(mv_tuple[0]) + \
                #             " to " + coords_to_alg(mv_tuple[1]) + ", gets promoted"
                self._popup_promo()
                return messageString

        # FLAG: it could be possible to capture "en passant" during the next move
        if (not capture) and (C_PAWN in self._prev_source_piece):
            if abs(self._prev_source_square[0] - self._prev_target_square[0]) > 1:
                self.pawn_jumped = True
                self.jumping_pawn_loc = self._prev_target_square
                if self._prev_target_square[0] > self._prev_source_square[0]:
                    self.jumped_over = (self._prev_source_square[0] + 1, self._prev_source_square[1])
                else:
                    self.jumped_over = (self._prev_source_square[0] - 1, self._prev_source_square[1])

        self._play_sequence += 1
        return messageString

    def finish_promotion(self, selected_piece):# TODO rather disp. this in the in-game console

        # msg = self.curr_player+'promoted to '+selected_piece
        # print(msg)
        self._play_sequence += 1
        self.tests_post_move()

    def tests_post_move(self):
        current_color = self.curr_player
        if ChessRules.is_checkmate(self, current_color):
            self.pev(chdefs.ChessEvents.Checkmate)
            # debug.print('PEV - checkmate')


        elif ChessRules.is_player_in_check(self, current_color):
            self.pev(chdefs.ChessEvents.Check)
            # debug.print('PEV - check')

    def undo_move(self):
        if (self._prev_source_square is None) or (self._prev_target_square is None):
            raise NotImplementedError('cannot undo more than 1 move, or undo when turn==0')

        self._load_serial(self._backup_serial)
        self._prev_source_square = None
        self._prev_target_square = None

        # reset
        self.pawn_jumped = False
        self.jumping_pawn_loc = None
        self.jumped_over = None


if __name__ == "__main__":
    testcode = int(input('What do you wish to test? 1 for rules, 2 for board, 3 serialize, 4 pieces pos > '))

    if testcode == 4:
        print()
        cb = ChessBoard(0)
        pt = input('wat type? ')
        col = input('wat color? ')
        print(cb.get_piece_positions(col, pt))

    elif testcode == 3:
        cb = ChessBoard(0)
        print(cb.serialize())

    elif testcode == 2:
        cb = ChessBoard(0)
        board1 = cb.state
        for r in range(8):
            for c in range(8):
                print(board1[r][c], end='')
            print("")

        print("Move piece test...")
        cb.move_piece(((0, 0), (4, 4)))
        board2 = cb.state
        for r in range(8):
            for c in range(8):
                print(board2[r][c], end='')
            print("")

    elif testcode == 1:
        cb = ChessBoard()
        rules = ChessRules()
        print(rules.is_checkmate(cb, C_WHITE_PLAYER))
        print(rules.is_clear_path(cb, (0, 0), (5, 5)))
        print(rules.is_clear_path(cb, (1, 1), (5, 5)))
