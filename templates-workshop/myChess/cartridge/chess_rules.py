from .ChessBoard import ChessBoard
from .chess_symbols import *


class ChessRules:
    valid_moves_cache = dict()

    @staticmethod
    def chebyshev_distance(from_pos, to_pos):
        # see https://en.wikipedia.org/wiki/Chebyshev_distance if needed
        return max(
            abs(from_pos[0] - to_pos[0]), abs(from_pos[1] - to_pos[1])
        )

    @staticmethod
    def clear_los_predicate(board, from_pos, to_pos):
        """
        LoS = Line of Sight

        The goal of that function is to return True whenever there is nothing in a straight line between
        from_pos and to_pos cells... Non-inclusive!
        Direction can be one out of three: horizontal, vertical, or diagonal

        :param board:
        :param from_pos:
        :param to_pos:
        :return:
        """
        if from_pos[0] == to_pos[0] and from_pos[1] == to_pos[1]:
            raise ValueError('ERROR! clear_los_predicate: receives one identical value for from_pos, to_pos params')
        if ChessRules.chebyshev_distance(from_pos, to_pos) < 2:
            print('*warning* Testing clear_los_predicate on two adjacent cells!')
            return True  # nothing is blocking line of sight, because line of sight doesnt exist

        # sometimes we'll need to swap from_pos and to_pos.
        # This preleminary step is to have less cases to handle (4 instead of 6)
        need_to_swap = False
        direction = 'diag'
        if not abs(from_pos[0] - to_pos[0]):
            direction = 'horz'
            if from_pos[1] > to_pos[1]:
                need_to_swap = True
        if not abs(from_pos[1] - to_pos[1]):
            direction = 'vert'
            if from_pos[0] > to_pos[0]:
                need_to_swap = True
        if direction == 'diag':
            if from_pos[0] > to_pos[0]:
                need_to_swap = True
        if need_to_swap:
            temp_var = to_pos
            to_pos = from_pos
            from_pos = temp_var
        if direction == 'diag':
            if from_pos[1] < to_pos[1]:
                direction = 'diag_down'
            else:
                direction = 'diag_up'

        all_increm_vectors = {
            'diag_down': (1, 1),
            'diag_up': (1, -1),
            'horz': (0, 1),
            'vert': (1, 0)
        }
        # - debug
        # print('PARAMS_TESTING:', from_pos, to_pos, direction)
        curr_cell = list(from_pos)
        adhoc_v = all_increm_vectors[direction]
        i_cap, j_cap = to_pos

        curr_cell[0] += adhoc_v[0]
        curr_cell[1] += adhoc_v[1]
        while not (curr_cell[0] == i_cap and curr_cell[1] == j_cap):
            # - debug
            # print('tested cell:', curr_cell[0], curr_cell[1])
            if board.state[curr_cell[1]][curr_cell[0]] != C_EMPTY_SQUARE:
                return False
            curr_cell[0] += adhoc_v[0]
            curr_cell[1] += adhoc_v[1]
        return True

    @staticmethod
    def piece_threatens(piece, board, source, dest) -> bool:
        """
        retunts True/False wether the given piece located at X controls/threatens the Y cell
        :param piece: describes a piece, for example 'wB' or 'bQ' (white bishop, or black Queen)
        :param board:
        :param source: the X cell, where the piece is located
        :param dest: the Y cell
        :return: True/False
        """
        # print('call piece_threatens !')
        # print(piece, board, source, dest)
        # print('...')
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        return False  # TODO fix!

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
                    if ChessRules.clear_los_predicate(board, from_tuple, to_tuple):
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
                    if ChessRules.clear_los_predicate(board, from_tuple, to_tuple):
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
                if ChessRules.clear_los_predicate(board, from_tuple, to_tuple):
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
                if ChessRules.clear_los_predicate(board, from_tuple, to_tuple):
                    return True

        elif board.square_has(from_tuple, C_QUEEN):
            # Queen
            if (toSquare_r == fromSquare_r or toSquare_c == fromSquare_c) and (
                    toPiece == C_EMPTY_SQUARE or (enemy_sym_color in toPiece)):
                if ChessRules.clear_los_predicate(board, from_tuple, to_tuple):
                    return True
            if (abs(toSquare_r - fromSquare_r) == abs(toSquare_c - fromSquare_c)) and (
                    toPiece == C_EMPTY_SQUARE or (enemy_sym_color in toPiece)):
                if ChessRules.clear_los_predicate(board, from_tuple, to_tuple):
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

        # Castling is different for white and black players:
        if chesscolor == C_WHITE_PLAYER:
            # Updating the if condition to verify if Castling is allowed for user

            # TODO : the problem here is that we still cannot call is_player_in_check,
            #  as it will create infinite recursion
            if not boardref.wK_moved:  # and not ChessRules.is_player_in_check(boardref, chesscolor):
                coords_short_castle = alg_to_coords('g1')
                coords_long_castle = alg_to_coords('c1')
                if to_sq == coords_short_castle and (not boardref.wR8_moved):  # Test short castling
                    if boardref.square_has(to_sq, C_EMPTY_SQUARE) and ChessRules.clear_los_predicate(boardref, from_sq,
                                                                                               to_sq):
                        # Called a new method to verify if it is safe for the user to castle.
                        if not ChessRules.is_king_threatened_after_move(boardref, chesscolor, from_sq, to_sq):
                            return True
                if to_sq == coords_long_castle and (not boardref.wR1_moved):  # Test long castling
                    if boardref.square_has(to_sq, C_EMPTY_SQUARE) and ChessRules.clear_los_predicate(boardref, from_sq,
                                                                                               to_sq):
                        # Called a new method to verify if it is safe for the user to castle.
                        if not ChessRules.is_king_threatened_after_move(boardref, chesscolor, from_sq, to_sq):
                            return True

        elif chesscolor == C_BLACK_PLAYER:
            # Updating the if condition to verify if Castling is allowed for user
            if not boardref.bK_moved and not ChessRules.is_player_in_check(boardref, chesscolor):
                coords_short_castle = alg_to_coords('g8')
                coords_long_castle = alg_to_coords('c8')
                if to_sq == coords_short_castle and (not boardref.bR8_moved):  # Test short castling
                    if boardref.square_has(to_sq, C_EMPTY_SQUARE) and ChessRules.clear_los_predicate(boardref, from_sq,
                                                                                               to_sq):
                        # Called a new method to verify if it is safe for the user to castle.
                        if not ChessRules.is_king_threatened_after_move(boardref, chesscolor, from_sq, to_sq):
                            return True
                if to_sq == coords_long_castle and (not boardref.bR1_moved):  # Test long castling
                    if boardref.square_has(to_sq, C_EMPTY_SQUARE) and ChessRules.clear_los_predicate(boardref, from_sq,
                                                                                               to_sq):
                        # Called a new method to verify if it is safe for the user to castle.
                        if not ChessRules.is_king_threatened_after_move(boardref, chesscolor, from_sq, to_sq):
                            return True

        return False

    # Method created to check if the king is under threat after the move to the new square in terms of castling.
    @staticmethod
    def is_king_threatened_after_move(boardref, chesscolor, from_sq, to_sq):
        # Make a temporary move
        from_piece = boardref.state[from_sq[0]][from_sq[1]]
        to_piece = boardref.state[to_sq[0]][to_sq[1]]
        boardref.state[to_sq[0]][to_sq[1]] = from_piece
        boardref.state[from_sq[0]][from_sq[1]] = C_EMPTY_SQUARE

        # Check if the king is threatened in the new position
        is_threatened = ChessRules.is_player_in_check(boardref, chesscolor)

        # Undo the temporary move
        boardref.state[from_sq[0]][from_sq[1]] = from_piece
        boardref.state[to_sq[0]][to_sq[1]] = to_piece

        return is_threatened

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

        # Check if any of enemy player's pieces is threatening the current player's king
        for row in range(8):
            for col in range(8):
                piece = board.state[row][col]
                if enemyColor in piece:
                    source = (row, col)
                    dest = kingTuple
                    if ChessRules.is_legal_move(board, enemyColorFull, (row, col), kingTuple):
                    # TODO break the cause of infinite recursion, by implementing a new func piece_threatens
                    # if ChessRules.piece_threatens(piece, board, source, dest):
                        return True
        return False
