"""
model for the game of chess (whats a chess Player/a chess Board +what are the rules?)
"""

__all__ = [
    'C_KING', 'C_QUEEN', 'C_ROOK', 'C_BISHOP', 'C_KNIGHT', 'C_PAWN',
    'C_BLACK_PLAYER', 'C_WHITE_PLAYER',
    'C_EMPTY_SQUARE',

    'ChessPlayer',
    'ChessBoard',
    'ChessRules'
]

C_KING, C_QUEEN, C_ROOK, C_BISHOP, C_KNIGHT, C_PAWN = 'K', 'Q', 'R', 'B', 'N', '_'
C_BLACK_PLAYER, C_WHITE_PLAYER = 'black', 'white'  # its better use such identifiers rather than str
C_EMPTY_SQUARE = 'ee'  # empty cell symbol

BOARDS_DEBUG = {
    'e.p.':  # pour tester "en passant"
        '\
bReebBbQbKbBbNbR\
eeb_b_b_b_b_b_b_\
b_eebNeeeeeeeeee\
eeeeeeeeeew_eeee\
eeeeeeeew_eeeeee\
eeeeeeeeeeeeeeee\
w_w_w_w_eeeew_w_\
wRwNwBwQwKwBwNwR\
5',
}


class ChessPlayer:
    @classmethod
    def conv_move(cls, packedcoords):
        """
        utility method so i can input moves such as 'e2e4' instead of ((4,1),(4,3))
        which is very un-natural
        """
        # print('call to conv_move -->', packedcoords)
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


class ChessRules:
    valid_moves_cache = dict()

    def is_checkmate(self, board_obj, chesscolor: str):
        """
        returns True if 'color' player is in checkmate, uses GetListOfValidMoves
        for each piece... If there aren't any valid moves, then return true
        """

        if chesscolor == C_BLACK_PLAYER:
            ch_color_sym = 'b'
        elif chesscolor == C_WHITE_PLAYER:
            ch_color_sym = 'w'
        else:
            raise ValueError('ERR: invalid chesscolor arg. passed to ChessRules.is_checkmate!')

        myColorValidMoves = list()
        for row in range(8):
            for col in range(8):
                piece = board_obj.state[row][col]
                if ch_color_sym in piece:
                    myColorValidMoves.extend(self.get_valid_moves(board_obj, chesscolor, (row, col)))
        return not len(myColorValidMoves)

    def get_valid_moves(self, board_obj, color, square_ij):
        board_hash = board_obj.serialize()
        cache = self.__class__.valid_moves_cache
        if board_hash in cache:
            if square_ij in cache[board_hash]:
                return cache[board_hash][square_ij]  # rule: never compute the same thing twice!
        else:
            cache[board_hash] = dict()

        legal_dest_spaces = list()
        for row in range(8):
            for column in range(8):
                candidate_m = (row, column)
                if self.is_legal_move(board_obj, color, square_ij, candidate_m):
                    if not self.puts_player_in_check(board_obj, color, square_ij, candidate_m):
                        legal_dest_spaces.append(candidate_m)

        cache[board_hash][square_ij] = legal_dest_spaces
        return legal_dest_spaces

    def is_legal_move(self, board, pl_chesscolor, fromTuple, toTuple):
        # print "IsLegalMove with fromTuple:",fromTuple,"and toTuple:",toTuple,"color = ",color
        fromSquare_r, fromSquare_c = fromTuple
        toSquare_r, toSquare_c = toTuple

        fromPiece = board.state[fromSquare_r][fromSquare_c]
        toPiece = board.state[toSquare_r][toSquare_c]

        if pl_chesscolor == C_BLACK_PLAYER:
            enemy_color = C_WHITE_PLAYER
            enemy_sym_color = 'w'
        elif pl_chesscolor == C_WHITE_PLAYER:
            enemy_color = C_BLACK_PLAYER
            enemy_sym_color = 'b'
        else:
            raise ValueError('ERR: wrong arg for color in ChessRules.is_legal_move')

        if fromTuple == toTuple:
            return False

        if C_PAWN in fromPiece:
            # Pawn
            if pl_chesscolor == C_BLACK_PLAYER:
                if toSquare_r == fromSquare_r + 1 and toSquare_c == fromSquare_c and toPiece == C_EMPTY_SQUARE:
                    # moving forward one space
                    return True
                if fromSquare_r == 1 and toSquare_r == fromSquare_r + 2 and toSquare_c == fromSquare_c and toPiece == C_EMPTY_SQUARE:
                    # black pawn on starting row can move forward 2 spaces if there is no one directly ahead
                    if self.is_clear_path(board, fromTuple, toTuple):
                        return True
                if board.jumped_over is not None:  # en passant
                    if (toSquare_r == fromSquare_r+1) and board.jumped_over[0] == toSquare_r and board.jumped_over[1] == toSquare_c:
                        return True
                if toSquare_r == fromSquare_r + 1 and (
                        toSquare_c == fromSquare_c + 1 or toSquare_c == fromSquare_c - 1):
                    if enemy_sym_color in toPiece:  # can attack
                        return True

            elif pl_chesscolor == C_WHITE_PLAYER:
                if toSquare_r == fromSquare_r - 1 and toSquare_c == fromSquare_c and toPiece == C_EMPTY_SQUARE:
                    # moving forward one space
                    return True
                if fromSquare_r == 6 and toSquare_r == fromSquare_r - 2 and toSquare_c == fromSquare_c and toPiece == C_EMPTY_SQUARE:
                    # black pawn on starting row can move forward 2 spaces if there is no one directly ahead
                    if self.is_clear_path(board, fromTuple, toTuple):
                        return True
                if board.jumped_over is not None:  # en passant
                    if (toSquare_r == fromSquare_r-1) and board.jumped_over[0] == toSquare_r and board.jumped_over[1] == toSquare_c:
                        return True
                if toSquare_r == fromSquare_r - 1 and (
                        toSquare_c == fromSquare_c + 1 or toSquare_c == fromSquare_c - 1):
                    if enemy_sym_color in toPiece:  # attacking
                        return True

        elif C_ROOK in fromPiece:
            # Rook
            if (toSquare_r == fromSquare_r or toSquare_c == fromSquare_c) and (
                    toPiece == C_EMPTY_SQUARE or (enemy_sym_color in toPiece)):
                if self.is_clear_path(board, fromTuple, toTuple):
                    return True

        elif C_KNIGHT in fromPiece:
            # Knight
            col_diff = toSquare_c - fromSquare_c
            row_diff = toSquare_r - fromSquare_r
            if toPiece == C_EMPTY_SQUARE or (enemy_sym_color in toPiece):
                if col_diff == 1 and row_diff == -2:
                    return True
                if col_diff == 2 and row_diff == -1:
                    return True
                if col_diff == 2 and row_diff == 1:
                    return True
                if col_diff == 1 and row_diff == 2:
                    return True
                if col_diff == -1 and row_diff == 2:
                    return True
                if col_diff == -2 and row_diff == 1:
                    return True
                if col_diff == -2 and row_diff == -1:
                    return True
                if col_diff == -1 and row_diff == -2:
                    return True

        elif C_BISHOP in fromPiece:
            # Bishop
            if (abs(toSquare_r - fromSquare_r) == abs(toSquare_c - fromSquare_c)) and (
                    toPiece == C_EMPTY_SQUARE or (enemy_sym_color in toPiece)):
                if self.is_clear_path(board, fromTuple, toTuple):
                    return True

        elif C_QUEEN in fromPiece:
            # Queen
            if (toSquare_r == fromSquare_r or toSquare_c == fromSquare_c) and (
                    toPiece == C_EMPTY_SQUARE or (enemy_sym_color in toPiece)):
                if self.is_clear_path(board, fromTuple, toTuple):
                    return True
            if (abs(toSquare_r - fromSquare_r) == abs(toSquare_c - fromSquare_c)) and (
                    toPiece == C_EMPTY_SQUARE or (enemy_sym_color in toPiece)):
                if self.is_clear_path(board, fromTuple, toTuple):
                    return True

        elif C_KING in fromPiece:
            # King
            col_diff = toSquare_c - fromSquare_c
            row_diff = toSquare_r - fromSquare_r
            if toPiece == C_EMPTY_SQUARE or (enemy_sym_color in toPiece):
                if abs(col_diff) == 1 and abs(row_diff) == 0:
                    return True
                if abs(col_diff) == 0 and abs(row_diff) == 1:
                    return True
                if abs(col_diff) == 1 and abs(row_diff) == 1:
                    return True

        return False  # if none of the other "True"s are hit above

    def puts_player_in_check(self, board_obj, color, fromTuple, toTuple):
        """
        makes a hypothetical move,
        returns True if it puts current player into check
        """

        fromSquare_r = fromTuple[0]
        fromSquare_c = fromTuple[1]
        toSquare_r = toTuple[0]
        toSquare_c = toTuple[1]
        fromPiece = board_obj.state[fromSquare_r][fromSquare_c]
        toPiece = board_obj.state[toSquare_r][toSquare_c]

        # make the move, then test if 'color' is in check
        board_obj.state[toSquare_r][toSquare_c] = fromPiece
        board_obj.state[fromSquare_r][fromSquare_c] = C_EMPTY_SQUARE

        retval = self.IsInCheck(board_obj, color)

        # undo temporary move
        board_obj.state[toSquare_r][toSquare_c] = toPiece
        board_obj.state[fromSquare_r][fromSquare_c] = fromPiece

        return retval

    def IsInCheck(self, board, color):
        # check if 'color' is in check
        # scan through squares for all enemy pieces; if there IsLegalMove to color's king, then return True.
        if color == "black":
            myColor = 'b'
            enemyColor = 'w'
            enemyColorFull = 'white'
        else:
            myColor = 'w'
            enemyColor = 'b'
            enemyColorFull = 'black'

        kingTuple = (0, 0)
        # First, get current player's king location
        for row in range(8):
            for col in range(8):
                piece = board.state[row][col]
                if 'K' in piece and myColor in piece:
                    kingTuple = (row, col)

        # Check if any of enemy player's pieces has a legal move to current player's king
        for row in range(8):
            for col in range(8):
                piece = board.state[row][col]
                if enemyColor in piece:
                    if self.is_legal_move(board, enemyColorFull, (row, col), kingTuple):
                        return True
        return False

    def is_clear_path(self, board, from_pos, to_pos):
        # Return true if there is nothing in a straight line between fromTuple and toTuple, non-inclusive
        # Direction could be +/- vertical, +/- horizontal, +/- diagonal
        fromSquare_r = from_pos[0]
        fromSquare_c = from_pos[1]
        toSquare_r = to_pos[0]
        toSquare_c = to_pos[1]
        fromPiece = board.state[fromSquare_r][fromSquare_c]

        if abs(fromSquare_r - toSquare_r) <= 1 and abs(fromSquare_c - toSquare_c) <= 1:
            # The base case: just one square apart
            return True
        else:
            if toSquare_r > fromSquare_r and toSquare_c == fromSquare_c:
                # vertical +
                newTuple = (fromSquare_r + 1, fromSquare_c)
            elif toSquare_r < fromSquare_r and toSquare_c == fromSquare_c:
                # vertical -
                newTuple = (fromSquare_r - 1, fromSquare_c)
            elif toSquare_r == fromSquare_r and toSquare_c > fromSquare_c:
                # horizontal +
                newTuple = (fromSquare_r, fromSquare_c + 1)
            elif toSquare_r == fromSquare_r and toSquare_c < fromSquare_c:
                # horizontal -
                newTuple = (fromSquare_r, fromSquare_c - 1)
            elif toSquare_r > fromSquare_r and toSquare_c > fromSquare_c:
                # diagonal "SE"
                newTuple = (fromSquare_r + 1, fromSquare_c + 1)
            elif toSquare_r > fromSquare_r and toSquare_c < fromSquare_c:
                # diagonal "SW"
                newTuple = (fromSquare_r + 1, fromSquare_c - 1)
            elif toSquare_r < fromSquare_r and toSquare_c > fromSquare_c:
                # diagonal "NE"
                newTuple = (fromSquare_r - 1, fromSquare_c + 1)
            elif toSquare_r < fromSquare_r and toSquare_c < fromSquare_c:
                # diagonal "NW"
                newTuple = (fromSquare_r - 1, fromSquare_c - 1)

        if board.state[newTuple[0]][newTuple[1]] == C_EMPTY_SQUARE:
            return self.is_clear_path(board, newTuple, to_pos)
        return False


class ChessBoard:
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

    @classmethod
    def to_algebraic_notation(cls, coords):
        row, col = coords
        # Converts (row,col) to algebraic notation
        # (row,col) format used in Python Chess code starts at (0,0) in the upper left.
        # Algebraic notation starts in the lower left and uses "a..h" for the column.
        return ChessBoard.to_algebraic_notation_col(col) + ChessBoard.to_algebraic_notation_row(row)

    @classmethod
    def to_algebraic_notation_row(cls, row):
        # (row,col) format used in Python Chess code starts at (0,0) in the upper left.
        # Algebraic notation starts in the lower left and uses "a..h" for the column.
        B = ['8', '7', '6', '5', '4', '3', '2', '1']
        return B[row]

    @classmethod
    def to_algebraic_notation_col(cls, col):
        # (row,col) format used in Python Chess code starts at (0,0) in the upper left.
        # Algebraic notation starts in the lower left and uses "a..h" for the column.
        A = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        return A[col]

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

    def move_piece(self, mv_tuple):
        """
        :param mv_tuple: can be something like ([1,1], [2,6])
        changes the state of the board
        """
        cls = self.__class__

        fromSquare_r, fromSquare_c = self._prev_source_square = mv_tuple[0]
        toSquare_r, toSquare_c = self._prev_target_square = mv_tuple[1]
        self._prev_player = self.curr_player
        self._prev_source_piece = self.squares[fromSquare_r][fromSquare_c]
        self._prev_target_piece = self.squares[toSquare_r][toSquare_c]
        fromPiece_fullString = self.GetFullString(self._prev_source_piece)
        toPiece_fullString = self.GetFullString(self._prev_target_piece)
        self._backup_serial = self.serialize()

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

                messageString = fromPiece_fullString + " from " + cls.to_algebraic_notation(mv_tuple[0]) + \
                                " captures " + toPiece_fullString + " at " + cls.to_algebraic_notation(
                    self.jumping_pawn_loc) + " (en passant)"
                # capitalize first character of messageString
                messageString = messageString[0].upper() + messageString[1:len(messageString)]

        # reset bc its not possible to take when its more than 1 turn
        # reset
        self.pawn_jumped = False
        self.jumping_pawn_loc = None
        self.jumped_over = None
        if en_passant:
            return messageString

        self.squares[fromSquare_r][fromSquare_c] = C_EMPTY_SQUARE  # square left
        self.squares[toSquare_r][toSquare_c] = self._prev_source_piece  # square newly taken
        self._play_sequence += 1

        if C_EMPTY_SQUARE == self._prev_target_piece:
            capture = False
            messageString = fromPiece_fullString + " moves from " + cls.to_algebraic_notation(mv_tuple[0]) + \
                            " to " + cls.to_algebraic_notation(mv_tuple[1])
        else:
            capture = True
            messageString = fromPiece_fullString + " from " + cls.to_algebraic_notation(mv_tuple[0]) + \
                            " captures " + toPiece_fullString + " at " + cls.to_algebraic_notation(
                mv_tuple[1]) + "!"

        # FLAG: it could be possible to capture "en passant" during the next move
        print(self._prev_source_piece)
        if (not capture) and (C_PAWN in self._prev_source_piece):
            if abs(self._prev_source_square[0] - self._prev_target_square[0]) > 1:
                self.pawn_jumped = True
                self.jumping_pawn_loc = self._prev_target_square
                if self._prev_target_square[0] > self._prev_source_square[0]:
                    self.jumped_over = (self._prev_source_square[0] + 1, self._prev_source_square[1])
                else:
                    self.jumped_over = (self._prev_source_square[0] - 1, self._prev_source_square[1])
                print('jumped:true, over:', self.jumped_over)

        # capitalize first character of messageString
        messageString = messageString[0].upper() + messageString[1:len(messageString)]
        return messageString

    def undo_move(self):
        if (self._prev_source_square is None) or (self._prev_target_square is None):
            raise NotImplementedError('cannot undo more than 1 move, or undo when turn==0')

        # i0, j0 = self._prev_source_square
        # self.squares[i0][j0] = self._prev_source_piece
        # i1, j1 = self._prev_target_square
        # self.squares[i1][j1] = self._prev_target_piece
        # self._play_sequence -= 1

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
