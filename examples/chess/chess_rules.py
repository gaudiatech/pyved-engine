C_KING, C_QUEEN, C_ROOK, C_BISHOP, C_KNIGHT, C_PAWN = 'K', 'Q', 'R', 'B', 'N', '_'
C_BLACK_PLAYER, C_WHITE_PLAYER = 'black', 'white'  # its better use such identifiers rather than str
C_EMPTY_SQUARE = 'ee'  # empty cell symbol


# ------------------------
#  five util. functions
# ------------------------
def enemy(x):
    return C_BLACK_PLAYER if (x == C_WHITE_PLAYER) else C_WHITE_PLAYER


def alg_to_coords(algebraic_id_sq):
    c0, c1 = algebraic_id_sq
    row = 8 - int(c1)
    col = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'].index(c0)
    return row, col


def to_algebraic_notation_row(row):
    # (row,col) format used in Python Chess code starts at (0,0) in the upper left.
    # Algebraic notation starts in the lower left and uses "a..h" for the column.
    B = ['8', '7', '6', '5', '4', '3', '2', '1']
    return B[row]


def to_algebraic_notation_col(col):
    # (row,col) format used in Python Chess code starts at (0,0) in the upper left.
    # Algebraic notation starts in the lower left and uses "a..h" for the column.
    A = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    return A[col]


def coords_to_alg(rowcol_idxes):
    row, col = rowcol_idxes
    # Converts (row,col) to algebraic notation
    # (row,col) format used in Python Chess code starts at (0,0) in the upper left.
    # Algebraic notation starts in the lower left and uses "a..h" for the column.
    return to_algebraic_notation_col(col) + to_algebraic_notation_row(row)


class ChessRules:
    valid_moves_cache = dict()

    @staticmethod
    def is_checkmate(board_obj, chesscolor: str):
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
                    myColorValidMoves.extend(ChessRules.get_valid_moves(board_obj, chesscolor, (row, col)))
        return not len(myColorValidMoves)

    @staticmethod
    def get_valid_moves(board_obj, color, square_ij):
        board_hash = board_obj.serialize()
        cache = ChessRules.valid_moves_cache
        if board_hash in cache:
            if square_ij in cache[board_hash]:
                return cache[board_hash][square_ij]  # rule: never compute the same thing twice!
        else:
            cache[board_hash] = dict()

        legal_dest_spaces = list()
        for row in range(8):
            for column in range(8):
                candidate_m = (row, column)
                if ChessRules.is_legal_move(board_obj, color, square_ij, candidate_m):
                    if not ChessRules.puts_player_in_check(board_obj, color, square_ij, candidate_m):
                        legal_dest_spaces.append(candidate_m)

        cache[board_hash][square_ij] = legal_dest_spaces
        return legal_dest_spaces

    @staticmethod
    def is_legal_move(board, pl_chesscolor, from_tuple, to_tuple) -> bool:
        """
        checks wether Yes/No the considered move is legal
        """
        # print "IsLegalMove with fromTuple:",fromTuple,"and toTuple:",toTuple,"color = ",color
        fromSquare_r, fromSquare_c = from_tuple
        toSquare_r, toSquare_c = to_tuple
        toPiece = board.state[toSquare_r][toSquare_c]

        if pl_chesscolor == C_BLACK_PLAYER:
            enemy_sym_color = 'w'
        elif pl_chesscolor == C_WHITE_PLAYER:

            enemy_sym_color = 'b'
        else:
            raise ValueError('ERR: wrong arg for color in ChessRules.is_legal_move')

        if from_tuple == to_tuple:
            return False

        if board.square_has(from_tuple, C_PAWN):
            # Pawn
            if pl_chesscolor == C_BLACK_PLAYER:
                if toSquare_r == fromSquare_r + 1 and toSquare_c == fromSquare_c and toPiece == C_EMPTY_SQUARE:
                    # moving forward one space
                    return True
                if fromSquare_r == 1 and toSquare_r == fromSquare_r + 2 and toSquare_c == fromSquare_c and toPiece == C_EMPTY_SQUARE:
                    # black pawn on starting row can move forward 2 spaces if there is no one directly ahead
                    if ChessRules.is_clear_path(board, from_tuple, to_tuple):
                        return True
                if board.jumped_over is not None:  # en passant
                    if (toSquare_r == fromSquare_r + 1) and board.jumped_over[0] == toSquare_r and board.jumped_over[
                        1] == toSquare_c:
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
                    if ChessRules.is_clear_path(board, from_tuple, to_tuple):
                        return True
                if board.jumped_over is not None:  # en passant
                    if (toSquare_r == fromSquare_r - 1) and board.jumped_over[0] == toSquare_r and board.jumped_over[
                        1] == toSquare_c:
                        return True
                if toSquare_r == fromSquare_r - 1 and (
                        toSquare_c == fromSquare_c + 1 or toSquare_c == fromSquare_c - 1):
                    if enemy_sym_color in toPiece:  # attacking
                        return True

        elif board.square_has(from_tuple, C_ROOK):
            # Rook
            if (toSquare_r == fromSquare_r or toSquare_c == fromSquare_c) and (
                    toPiece == C_EMPTY_SQUARE or (enemy_sym_color in toPiece)):
                if ChessRules.is_clear_path(board, from_tuple, to_tuple):
                    return True

        elif board.square_has(from_tuple, C_KNIGHT):
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

        elif board.square_has(from_tuple, C_BISHOP):
            # Bishop
            if (abs(toSquare_r - fromSquare_r) == abs(toSquare_c - fromSquare_c)) and (
                    toPiece == C_EMPTY_SQUARE or (enemy_sym_color in toPiece)):
                if ChessRules.is_clear_path(board, from_tuple, to_tuple):
                    return True

        elif board.square_has(from_tuple, C_QUEEN):
            # Queen
            if (toSquare_r == fromSquare_r or toSquare_c == fromSquare_c) and (
                    toPiece == C_EMPTY_SQUARE or (enemy_sym_color in toPiece)):
                if ChessRules.is_clear_path(board, from_tuple, to_tuple):
                    return True
            if (abs(toSquare_r - fromSquare_r) == abs(toSquare_c - fromSquare_c)) and (
                    toPiece == C_EMPTY_SQUARE or (enemy_sym_color in toPiece)):
                if ChessRules.is_clear_path(board, from_tuple, to_tuple):
                    return True

        elif board.square_has(from_tuple, C_KING):
            return ChessRules.is_valid_king_move(board, pl_chesscolor, from_tuple, to_tuple)

        return False  # if none of the other "True"s are hit above

    @staticmethod
    def is_valid_king_move(boardref, chesscolor, from_sq, to_sq):
        """
        encoding valid king moves
        """
        # -----
        # [easy case]
        # if move distance==1, i.e. move is a (8-dir) move to an adjacent square => ok
        # -----
        row0, col0 = from_sq
        row1, col1 = to_sq
        dt_row = abs(row0 - row1)
        dt_col = abs(col0 - col1)
        if boardref.square_has(to_sq, C_EMPTY_SQUARE) or boardref.square_ctrled_by(to_sq, enemy(chesscolor)):
            if (1 == dt_col and 0 == dt_row) or (0 == dt_col and 1 == dt_row):
                return True
            if 1 == dt_col and 1 == dt_row:
                return True

        # test du roque est pas pareil selon blancs ou noirs:
        if chesscolor == C_WHITE_PLAYER:
            if not boardref.wK_moved:  # and not ChessRules.is_player_in_check(boardref, chesscolor):
                # TODO cmt vérifier que rien fait échec sur la ligne de deplacement?
                coords_pt_roque = alg_to_coords('g1')
                coords_gd_roque = alg_to_coords('c1')
                if to_sq == coords_pt_roque and (not boardref.wR8_moved):  # test petit roque
                    if boardref.square_has(to_sq, C_EMPTY_SQUARE) and ChessRules.is_clear_path(boardref, from_sq,
                                                                                               to_sq):
                        return True
                if to_sq == coords_gd_roque and (not boardref.wR1_moved):  # test petit roque
                    if boardref.square_has(to_sq, C_EMPTY_SQUARE) and ChessRules.is_clear_path(boardref, from_sq,
                                                                                               to_sq):
                        return True

        elif chesscolor == C_BLACK_PLAYER:
            if not boardref.bK_moved:  # and not ChessRules.is_player_in_check(boardref, chesscolor):
                # TODO cmt vérifier que rien fait échec sur la ligne de deplacement?
                coords_pt_roque = alg_to_coords('g8')
                coords_gd_roque = alg_to_coords('c8')
                if to_sq == coords_pt_roque and (not boardref.bR8_moved):  # test petit roque
                    if boardref.square_has(to_sq, C_EMPTY_SQUARE) and ChessRules.is_clear_path(boardref, from_sq,
                                                                                               to_sq):
                        return True
                if to_sq == coords_gd_roque and (not boardref.bR1_moved):  # test petit roque
                    if boardref.square_has(to_sq, C_EMPTY_SQUARE) and ChessRules.is_clear_path(boardref, from_sq,
                                                                                               to_sq):
                        return True

        return False

    @staticmethod
    def puts_player_in_check(board_obj, color, fromTuple, toTuple):
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

        retval = ChessRules.is_player_in_check(board_obj, color)

        # undo temporary move
        board_obj.state[toSquare_r][toSquare_c] = toPiece
        board_obj.state[fromSquare_r][fromSquare_c] = fromPiece

        return retval

    @staticmethod
    def is_player_in_check(board, color):
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
                    if ChessRules.is_legal_move(board, enemyColorFull, (row, col), kingTuple):
                        return True
        return False

    @staticmethod
    def is_clear_path(board, from_pos, to_pos):
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

        # TODO wtf ? recursive isnt good here
        if board.state[newTuple[0]][newTuple[1]] == C_EMPTY_SQUARE:
            return ChessRules.is_clear_path(board, newTuple, to_pos)
        return False
