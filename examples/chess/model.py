"""
model for the game of chess (whats a chess Player/a chess Board +what are the rules?)
"""

C_BLACK, C_WHITE = 'black', 'white'  # its better use such identifiers rather than str
EC_SYM = 'ee'  # empty cell symbol


class BaseChessPlayer:
    @classmethod
    def conv_move(cls, packedcoords):
        """
        utility method so i can input moves such as 'e2e4' instead of ((4,1),(4,3))
        which is very un-natural
        """
        print('call to conv_move -->', packedcoords)
        if len(packedcoords) != 4:
            raise ValueError('arg passed to ChessAI.conv_move has not the expected format! Received:', packedcoords)
        li_given_char = list(packedcoords)
        ref = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        t1 = [8 - int(li_given_char[1]), ref.index(li_given_char[0])]
        t2 = [8 - int(li_given_char[3]), ref.index(li_given_char[2])]
        return tuple(t1), tuple(t2)

    def __init__(self, name, color: str):
        self._name = name
        if color not in (C_BLACK, C_WHITE):
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

    def is_checkmate(self, board, chesscolor: str):
        """
        returns True if 'color' player is in checkmate, uses GetListOfValidMoves
        for each piece... If there aren't any valid moves, then return true
        """

        if chesscolor == C_BLACK:
            ch_color_sym = 'b'
        elif chesscolor == C_WHITE:
            ch_color_sym = 'w'
        else:
            raise ValueError('ERR: invalid chesscolor arg. passed to ChessRules.is_checkmate!')

        myColorValidMoves = list()
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if ch_color_sym in piece:
                    myColorValidMoves.extend(self.GetListOfValidMoves(board, chesscolor, (row, col)))
        return not len(myColorValidMoves)

    def GetListOfValidMoves(self, board, color, fromTuple):
        legalDestinationSpaces = list()
        for row in range(8):
            for col in range(8):
                d = (row, col)
                if self.is_legal_move(board, color, fromTuple, d):
                    if not self.DoesMovePutPlayerInCheck(board, color, fromTuple, d):
                        legalDestinationSpaces.append(d)
        return legalDestinationSpaces

    def is_legal_move(self, board, color, fromTuple, toTuple):
        # print "IsLegalMove with fromTuple:",fromTuple,"and toTuple:",toTuple,"color = ",color
        fromSquare_r = fromTuple[0]
        fromSquare_c = fromTuple[1]
        toSquare_r = toTuple[0]
        toSquare_c = toTuple[1]
        fromPiece = board[fromSquare_r][fromSquare_c]
        toPiece = board[toSquare_r][toSquare_c]

        if color == C_BLACK:
            enemy_color = C_WHITE
            enemy_sym_color = 'w'
        elif color == C_WHITE:
            enemy_color = C_BLACK
            enemy_sym_color = 'b'
        else:
            raise ValueError('ERR: wrong arg for color in ChessRules.is_legal_move')

        if fromTuple == toTuple:
            return False

        if "P" in fromPiece:
            # Pawn
            if color == "black":
                if toSquare_r == fromSquare_r + 1 and toSquare_c == fromSquare_c and toPiece == EC_SYM:
                    # moving forward one space
                    return True
                if fromSquare_r == 1 and toSquare_r == fromSquare_r + 2 and toSquare_c == fromSquare_c and toPiece == EC_SYM:
                    # black pawn on starting row can move forward 2 spaces if there is no one directly ahead
                    if self.is_clear_path(board, fromTuple, toTuple):
                        return True
                if toSquare_r == fromSquare_r + 1 and (
                        toSquare_c == fromSquare_c + 1 or toSquare_c == fromSquare_c - 1) and (
                        enemy_sym_color in toPiece):  # attacking
                    return True

            elif color == "white":
                if toSquare_r == fromSquare_r - 1 and toSquare_c == fromSquare_c and toPiece == EC_SYM:
                    # moving forward one space
                    return True
                if fromSquare_r == 6 and toSquare_r == fromSquare_r - 2 and toSquare_c == fromSquare_c and toPiece == EC_SYM:
                    # black pawn on starting row can move forward 2 spaces if there is no one directly ahead
                    if self.is_clear_path(board, fromTuple, toTuple):
                        return True
                if toSquare_r == fromSquare_r - 1 and (
                        toSquare_c == fromSquare_c + 1 or toSquare_c == fromSquare_c - 1) and (
                        enemy_sym_color in toPiece):  # attacking
                    return True

        elif "R" in fromPiece:
            # Rook
            if (toSquare_r == fromSquare_r or toSquare_c == fromSquare_c) and (
                    toPiece == EC_SYM or (enemy_sym_color in toPiece)):
                if self.is_clear_path(board, fromTuple, toTuple):
                    return True

        elif "T" in fromPiece:
            # Knight
            col_diff = toSquare_c - fromSquare_c
            row_diff = toSquare_r - fromSquare_r
            if toPiece == EC_SYM or (enemy_sym_color in toPiece):
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

        elif "B" in fromPiece:
            # Bishop
            if (abs(toSquare_r - fromSquare_r) == abs(toSquare_c - fromSquare_c)) and (
                    toPiece == EC_SYM or (enemy_sym_color in toPiece)):
                if self.is_clear_path(board, fromTuple, toTuple):
                    return True

        elif "Q" in fromPiece:
            # Queen
            if (toSquare_r == fromSquare_r or toSquare_c == fromSquare_c) and (
                    toPiece == EC_SYM or (enemy_sym_color in toPiece)):
                if self.is_clear_path(board, fromTuple, toTuple):
                    return True
            if (abs(toSquare_r - fromSquare_r) == abs(toSquare_c - fromSquare_c)) and (
                    toPiece == EC_SYM or (enemy_sym_color in toPiece)):
                if self.is_clear_path(board, fromTuple, toTuple):
                    return True

        elif "K" in fromPiece:
            # King
            col_diff = toSquare_c - fromSquare_c
            row_diff = toSquare_r - fromSquare_r
            if toPiece == EC_SYM or (enemy_sym_color in toPiece):
                if abs(col_diff) == 1 and abs(row_diff) == 0:
                    return True
                if abs(col_diff) == 0 and abs(row_diff) == 1:
                    return True
                if abs(col_diff) == 1 and abs(row_diff) == 1:
                    return True

        return False  # if none of the other "True"s are hit above

    def DoesMovePutPlayerInCheck(self, board, color, fromTuple, toTuple):
        """
        makes a hypothetical move,
        returns True if it puts current player into check
        """

        fromSquare_r = fromTuple[0]
        fromSquare_c = fromTuple[1]
        toSquare_r = toTuple[0]
        toSquare_c = toTuple[1]
        fromPiece = board[fromSquare_r][fromSquare_c]
        toPiece = board[toSquare_r][toSquare_c]

        # make the move, then test if 'color' is in check
        board[toSquare_r][toSquare_c] = fromPiece
        board[fromSquare_r][fromSquare_c] = EC_SYM

        retval = self.IsInCheck(board, color)

        # undo temporary move
        board[toSquare_r][toSquare_c] = toPiece
        board[fromSquare_r][fromSquare_c] = fromPiece

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
                piece = board[row][col]
                if 'K' in piece and myColor in piece:
                    kingTuple = (row, col)

        # Check if any of enemy player's pieces has a legal move to current player's king
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
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
        fromPiece = board[fromSquare_r][fromSquare_c]

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

        if board[newTuple[0]][newTuple[1]] == EC_SYM:
            return self.is_clear_path(board, newTuple, to_pos)
        return False


class ChessBoard:
    """
    Board layout; contains what pieces are present at each square
    """
    EMPTY_SYM = 'ee'

    def __init__(self, setup_type=0, serial=None):
        self._turn = 0
        self.squares = list()
        for _ in range(8):
            row = [self.EMPTY_SYM] * 8
            self.squares.append(row)

        if setup_type == 0:
            self.squares[0] = ['bR', 'bT', 'bB', 'bQ', 'bK', 'bB', 'bT', 'bR']
            self.squares[1] = ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP']

            self.squares[6] = ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP']
            self.squares[7] = ['wR', 'wT', 'wB', 'wQ', 'wK', 'wB', 'wT', 'wR']

        # Debugging set-ups
        # Testing IsLegalMove
        if setup_type == 1:
            self.squares[0] = ['bR', 'bT', 'bB', 'bQ', 'bK', 'bB', 'bT', 'bR']

            self.squares[6] = ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP']
            self.squares[7] = ['wR', 'wT', 'wB', 'wQ', 'wK', 'wB', 'wT', 'wR']

        # Testing IsInCheck, Checkmate
        if setup_type == 2:
            self.squares[2][4] = 'bK'
            self.squares[3][4] = 'bR'
            self.squares[4][2] = 'bB'
            self.squares[4][6] = 'wR'
            self.squares[6][0] = 'wB'
            self.squares[7] = [EC_SYM, EC_SYM, EC_SYM, 'wK', 'wQ', EC_SYM, 'wT', EC_SYM]

        # Testing Defensive AI
        if setup_type == 3:
            self.squares[2][4] = 'bK'
            self.squares[3][4] = 'bR'
            self.squares[4][2] = 'bB'
            self.squares[4][6] = 'wR'
            self.squares[7] = [EC_SYM, EC_SYM, EC_SYM, 'wK', 'wQ', EC_SYM, 'wT', EC_SYM]

    def serialize(self):
        serial = ''
        for j in range(8):
            for i in range(8):
                serial += self.squares[j][i]
        serial += str(self._turn)
        return serial

    @property
    def turn(self):
        return self._turn

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

    def ConvertToAlgebraicNotation(self, coords):
        row, col = coords
        # Converts (row,col) to algebraic notation
        # (row,col) format used in Python Chess code starts at (0,0) in the upper left.
        # Algebraic notation starts in the lower left and uses "a..h" for the column.
        return self.ConvertToAlgebraicNotation_col(col) + self.ConvertToAlgebraicNotation_row(row)

    def ConvertToAlgebraicNotation_row(self, row):
        # (row,col) format used in Python Chess code starts at (0,0) in the upper left.
        # Algebraic notation starts in the lower left and uses "a..h" for the column.
        B = ['8', '7', '6', '5', '4', '3', '2', '1']
        return B[row]

    def ConvertToAlgebraicNotation_col(self, col):
        # (row,col) format used in Python Chess code starts at (0,0) in the upper left.
        # Algebraic notation starts in the lower left and uses "a..h" for the column.
        A = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        return A[col]

    def GetFullString(self, p):
        if 'b' in p:
            name = "black "
        else:
            name = "white "

        if 'P' in p:
            name = name + "pawn"
        if 'R' in p:
            name = name + "rook"
        if 'T' in p:
            name = name + "knight"
        if 'B' in p:
            name = name + "bishop"
        if 'Q' in p:
            name = name + "queen"
        if 'K' in p:
            name = name + "king"

        return name

    def move_piece(self, moveTuple):
        fromSquare_r = moveTuple[0][0]
        fromSquare_c = moveTuple[0][1]
        toSquare_r = moveTuple[1][0]
        toSquare_c = moveTuple[1][1]

        fromPiece = self.squares[fromSquare_r][fromSquare_c]
        toPiece = self.squares[toSquare_r][toSquare_c]

        self.squares[toSquare_r][toSquare_c] = fromPiece
        self.squares[fromSquare_r][fromSquare_c] = EC_SYM

        fromPiece_fullString = self.GetFullString(fromPiece)
        toPiece_fullString = self.GetFullString(toPiece)

        if toPiece == EC_SYM:
            messageString = fromPiece_fullString + " moves from " + self.ConvertToAlgebraicNotation(moveTuple[0]) + \
                            " to " + self.ConvertToAlgebraicNotation(moveTuple[1])
        else:
            messageString = fromPiece_fullString + " from " + self.ConvertToAlgebraicNotation(moveTuple[0]) + \
                            " captures " + toPiece_fullString + " at " + self.ConvertToAlgebraicNotation(
                moveTuple[1]) + "!"

        # capitalize first character of messageString
        tmp = messageString[0].upper() + messageString[1:len(messageString)]
        messageString = tmp

        self._turn += 1

        return messageString


if __name__ == "__main__":
    testcode = int(input('What do you wish to test? 1 for rules, 2 for board, 3 serialize > '))
    if testcode == 3:
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
        print(rules.is_checkmate(cb.state, C_WHITE))
        print(rules.is_clear_path(cb.state, (0, 0), (5, 5)))
        print(rules.is_clear_path(cb.state, (1, 1), (5, 5)))
