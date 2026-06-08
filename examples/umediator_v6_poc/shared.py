from __future__ import annotations

BOARD_SIZE = 7
WINDOW_SIZE = 700
MARGIN = 40
GRID_SIZE = WINDOW_SIZE - 2 * MARGIN
CELL_SIZE = GRID_SIZE // BOARD_SIZE
GRID_SIZE = CELL_SIZE * BOARD_SIZE

BG_COLOR = (22, 62, 40)
GRID_COLOR = (240, 224, 180)
BLACK_COLOR = (20, 20, 20)
WHITE_COLOR = (235, 235, 235)
HINT_COLOR = (210, 220, 120)

PLAYER_BLACK = "black"
PLAYER_WHITE = "white"
PLAYERS = (PLAYER_BLACK, PLAYER_WHITE)

CELL_TO_COLOR = {
    PLAYER_BLACK: BLACK_COLOR,
    PLAYER_WHITE: WHITE_COLOR,
}

EMPTY = 0
BLACK = 1
WHITE = 2


def opponent(player):
    return PLAYER_WHITE if player == PLAYER_BLACK else PLAYER_BLACK


def player_to_cell(player):
    return BLACK if player == PLAYER_BLACK else WHITE


def cell_to_player(cell_value):
    if cell_value == BLACK:
        return PLAYER_BLACK
    if cell_value == WHITE:
        return PLAYER_WHITE
    return None


def new_board():
    board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    board[0][0] = BLACK
    board[BOARD_SIZE - 1][BOARD_SIZE - 1] = BLACK
    board[0][BOARD_SIZE - 1] = WHITE
    board[BOARD_SIZE - 1][0] = WHITE
    return board


def new_state():
    return {
        "board": new_board(),
        "turn": PLAYER_BLACK,
        "winner": None,
        "move_count": 0,
        "last_move": None,
    }


def copy_board(board):
    return [row[:] for row in board]


def board_full(board):
    for row in board:
        for cell in row:
            if cell == EMPTY:
                return False
    return True


def count_pieces(board):
    black = white = 0
    for row in board:
        for cell in row:
            if cell == BLACK:
                black += 1
            elif cell == WHITE:
                white += 1
    return black, white


def winner_from_board(board):
    black, white = count_pieces(board)
    if black > white:
        return PLAYER_BLACK
    if white > black:
        return PLAYER_WHITE
    return "draw"


def in_bounds(row, col):
    return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE


def neighbors(row, col):
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr = row + dr
            nc = col + dc
            if in_bounds(nr, nc):
                yield nr, nc


def legal_moves(board, player):
    target = player_to_cell(player)
    moves = []
    seen = set()
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] != target:
                continue
            for nr, nc in neighbors(row, col):
                if board[nr][nc] == EMPTY and (nr, nc) not in seen:
                    seen.add((nr, nc))
                    moves.append((nr, nc))
    return moves


def is_legal_move(board, player, row, col):
    return (row, col) in legal_moves(board, player)


def apply_move(state, player, row, col):
    board = state["board"]
    if state["winner"] is not None:
        return False
    if state["turn"] != player:
        return False
    if not in_bounds(row, col):
        return False
    if board[row][col] != EMPTY:
        return False
    if not is_legal_move(board, player, row, col):
        return False

    color = player_to_cell(player)
    board[row][col] = color
    for nr, nc in neighbors(row, col):
        if board[nr][nc] != EMPTY and board[nr][nc] != color:
            board[nr][nc] = color

    state["move_count"] += 1
    state["last_move"] = (row, col, player)

    if board_full(board):
        state["winner"] = winner_from_board(board)
    else:
        state["turn"] = opponent(player)

    return True


def serialize_state(state):
    return {
        "board": copy_board(state["board"]),
        "turn": state["turn"],
        "winner": state["winner"],
        "move_count": state["move_count"],
        "last_move": state["last_move"],
    }


def cell_from_pos(pos):
    x, y = pos
    board_left = MARGIN
    board_top = MARGIN
    board_right = board_left + GRID_SIZE
    board_bottom = board_top + GRID_SIZE
    if not (board_left <= x <= board_right and board_top <= y <= board_bottom):
        return None

    col = int((x - board_left) // CELL_SIZE)
    row = int((y - board_top) // CELL_SIZE)
    if in_bounds(row, col):
        return row, col
    return None


def cell_center(row, col):
    return (
        MARGIN + col * CELL_SIZE + CELL_SIZE // 2,
        MARGIN + row * CELL_SIZE + CELL_SIZE // 2,
    )
