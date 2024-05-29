

C_KING, C_QUEEN, C_ROOK, C_BISHOP, C_KNIGHT, C_PAWN = 'K', 'Q', 'R', 'B', 'N', '_'
C_BLACK_PLAYER, C_WHITE_PLAYER = 'black', 'white'  # its better use such identifiers rather than str
C_EMPTY_SQUARE = 'ee'  # empty cell symbol


# ------------------------
#  five util. functions
# ------------------------
def to_algebraic_notation_row(row):  # used by the view
    # (row,col) format used in Python Chess code starts at (0,0) in the upper left.
    # Algebraic notation starts in the lower left and uses "a..h" for the column.
    B = ['8', '7', '6', '5', '4', '3', '2', '1']
    return B[row]


def to_algebraic_notation_col(col):  # also used by the view
    # (row,col) format used in Python Chess code starts at (0,0) in the upper left.
    # Algebraic notation starts in the lower left and uses "a..h" for the column.
    A = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    return A[col]


def alg_to_coords(algebraic_id_sq):
    c0, c1 = algebraic_id_sq
    row = 8 - int(c1)
    col = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'].index(c0)
    return row, col


def coords_to_alg(rowcol_idxes):
    row, col = rowcol_idxes
    # Converts (row,col) to algebraic notation
    # (row,col) format used in Python Chess code starts at (0,0) in the upper left.
    # Algebraic notation starts in the lower left and uses "a..h" for the column.
    return to_algebraic_notation_col(col) + to_algebraic_notation_row(row)


def enemy(x):
    return C_BLACK_PLAYER if (x == C_WHITE_PLAYER) else C_WHITE_PLAYER
