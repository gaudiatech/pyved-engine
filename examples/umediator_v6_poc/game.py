from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
THIS_DIR = Path(__file__).resolve().parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))


import pyved_engine as pyv

pyv.bootstrap_e()

from pyved_engine.umediator import Delivery, UMediator

from shared import (
    BG_COLOR,
    BLACK,
    BLACK_COLOR,
    BOARD_SIZE,
    CELL_SIZE,
    GRID_COLOR,
    HINT_COLOR,
    MARGIN,
    PLAYER_BLACK,
    PLAYER_WHITE,
    WHITE_COLOR,
    apply_move,
    cell_center,
    cell_from_pos,
    count_pieces,
    legal_moves,
    new_state,
    serialize_state,
)
from transport import build_transport


MOVE_REQUESTED = "virus.move_requested"
STATE_UPDATED = "virus.state_updated"
SYNC_REQUESTED = "virus.sync_requested"

MODE = "solo"
TRANSPORT_KIND = "auto"
HOST = "127.0.0.1"
PORT = 5005
PLAYER_COLOR = PLAYER_BLACK
SCREEN = None
MEDIATOR = None
GAME = None
TRANSPORT = None


def build_title():
    turn = GAME.state["turn"]
    winner = GAME.state["winner"]
    black_count, white_count = count_pieces(GAME.state["board"])
    parts = ["Virus", MODE]
    if MODE == "client":
        parts.append(f"player={PLAYER_COLOR}")
    if MODE != "solo":
        parts.append(f"{HOST}:{PORT}")
        parts.append(f"transport={TRANSPORT_KIND}")
    parts.append(f"turn={turn}")
    parts.append(f"{black_count}-{white_count}")
    if winner is not None:
        parts.append(f"winner={winner}")
    return " | ".join(parts)


class VirusMatch:
    def __init__(self, mediator, mode: str, player_color: str | None = None):
        self.mediator = mediator
        self.mode = mode
        self.player_color = player_color
        self.state = new_state()

        self.mediator.register(STATE_UPDATED, self._on_state_updated)
        self.mediator.register(MOVE_REQUESTED, self._on_move_requested)
        self.mediator.register(SYNC_REQUESTED, self._on_sync_requested)

    @property
    def is_server(self):
        return bool(self.mediator.network_layer and self.mediator.is_server)

    @property
    def is_client(self):
        return bool(self.mediator.network_layer and not self.mediator.is_server)

    def bootstrap(self):
        self._publish_state(local_only=True)
        self.mediator.update()
        if self.is_client:
            self.mediator.post(SYNC_REQUESTED, {}, delivery=Delivery.TO_SERVER)

    def _publish_state(self, local_only=False):
        payload = serialize_state(self.state)
        if local_only or self.mediator.network_layer is None:
            delivery = Delivery.LOCAL
        else:
            delivery = Delivery.BROADCAST if self.mediator.is_server else Delivery.LOCAL
        self.mediator.post(STATE_UPDATED, payload, delivery=delivery)

    def _on_state_updated(self, envelope):
        payload = envelope.payload
        self.state = {
            "board": [row[:] for row in payload["board"]],
            "turn": payload["turn"],
            "winner": payload["winner"],
            "move_count": payload["move_count"],
            "last_move": tuple(payload["last_move"]) if payload["last_move"] is not None else None,
        }

    def _on_sync_requested(self, envelope):
        if self.mediator.is_server:
            self._publish_state(local_only=False)

    def _on_move_requested(self, envelope):
        if self.mediator.network_layer is not None and not self.mediator.is_server:
            return

        payload = envelope.payload
        row = payload["row"]
        col = payload["col"]
        if self.state["winner"] is not None:
            return
        current_player = self.state["turn"]
        if apply_move(self.state, current_player, row, col):
            self._publish_state(local_only=False)

    def request_move(self, row, col):
        if self.state["winner"] is not None:
            return
        if self.mode == "client" and self.player_color is not None and self.player_color != self.state["turn"]:
            return

        delivery = Delivery.TO_SERVER if self.is_client else Delivery.LOCAL
        self.mediator.post(MOVE_REQUESTED, {"row": row, "col": col}, delivery=delivery)

    def legal_hints(self):
        return legal_moves(self.state["board"], self.state["turn"])


def draw_board(screen, game):
    screen.fill(BG_COLOR)
    left = MARGIN
    top = MARGIN
    size = CELL_SIZE * BOARD_SIZE
    right = left + size
    bottom = top + size

    for idx in range(BOARD_SIZE + 1):
        x = left + idx * CELL_SIZE
        y = top + idx * CELL_SIZE
        pyv.draw_line(screen, GRID_COLOR, (x, top), (x, bottom), 2)
        pyv.draw_line(screen, GRID_COLOR, (left, y), (right, y), 2)

    if game.state["winner"] is None:
        for row, col in game.legal_hints():
            pyv.draw_circle(screen, HINT_COLOR, cell_center(row, col), CELL_SIZE // 8, 2)

    board = game.state["board"]
    radius = CELL_SIZE // 3
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            cell = board[row][col]
            if cell == 0:
                continue
            color = BLACK_COLOR if cell == BLACK else WHITE_COLOR
            pyv.draw_circle(screen, color, cell_center(row, col), radius)
            pyv.draw_circle(screen, GRID_COLOR, cell_center(row, col), radius, 2)

    last_move = game.state["last_move"]
    if last_move is not None:
        row, col, _player = last_move
        pyv.draw_circle(screen, HINT_COLOR, cell_center(row, col), CELL_SIZE // 2 - 4, 2)


@pyv.declare_begin
def prep_game(vmst=None):
    global SCREEN, MEDIATOR, GAME, TRANSPORT

    pyv.init()
    SCREEN = pyv.get_surface()
    if MODE == "solo":
        MEDIATOR = UMediator()
    else:
        TRANSPORT = build_transport(TRANSPORT_KIND, "client", HOST, PORT)
        MEDIATOR = UMediator(TRANSPORT)
        TRANSPORT.start_comms(HOST, PORT)
    GAME = VirusMatch(MEDIATOR, mode=MODE, player_color=PLAYER_COLOR if MODE == "client" else None)
    GAME.bootstrap()


@pyv.declare_update
def update_game(time_info=None):
    dt = pyv.vars.clock.tick(60)
    del dt

    for event in pyv.fetch_events():
        if event.type == pyv.pygame.QUIT:
            pyv.vars.gameover = True
            return
        if event.type == pyv.pygame.KEYDOWN and event.key == pyv.pygame.K_ESCAPE:
            pyv.vars.gameover = True
            return
        if event.type == pyv.pygame.MOUSEBUTTONDOWN and event.button == 1:
            cell = cell_from_pos(event.pos)
            if cell is not None:
                row, col = cell
                GAME.request_move(row, col)

    MEDIATOR.update()
    draw_board(SCREEN, GAME)
    pyv.pygame.display.set_caption(build_title())
    pyv.flip()


@pyv.declare_end
def cleanup_game(vmst=None):
    global TRANSPORT

    if TRANSPORT is not None:
        TRANSPORT.shutdown_comms()
        TRANSPORT = None
    pyv.close_game()


def parse_args():
    parser = argparse.ArgumentParser(description="Tiny umediator v6 POC: le jeu du virus")
    parser.add_argument("--mode", choices=("solo", "client"), default="solo")
    parser.add_argument("--transport", choices=("auto", "socket", "ws"), default="auto")
    parser.add_argument("--force-ws", action="store_true", help="force the engine to select websocket transport")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5005)
    parser.add_argument("--player", choices=(PLAYER_BLACK, PLAYER_WHITE), default=PLAYER_BLACK)
    return parser.parse_args()


def main():
    global MODE, TRANSPORT_KIND, HOST, PORT, PLAYER_COLOR

    args = parse_args()
    MODE = args.mode
    TRANSPORT_KIND = args.transport
    HOST = args.host
    PORT = args.port
    PLAYER_COLOR = args.player

    configure_transport_flags(args.force_ws)
    pyv.run_game()


if __name__ == "__main__":
    main()
