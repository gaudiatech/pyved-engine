from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
THIS_DIR = Path(__file__).resolve().parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))


import pygame

from pyved_engine.umediator import Delivery, UMediator
from pyved_engine.umediator import netlayer_factory

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
    WHITE,
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


def build_title(mode, state, player_color=None, host=None, port=None):
    turn = state["turn"]
    winner = state["winner"]
    black_count, white_count = count_pieces(state["board"])

    parts = ["Virus", mode]
    if player_color is not None:
        parts.append(f"player={player_color}")
    if host is not None and port is not None:
        parts.append(f"{host}:{port}")
    parts.append(f"turn={turn}")
    parts.append(f"{black_count}-{white_count}")
    if winner is not None:
        parts.append(f"winner={winner}")
    return " | ".join(parts)


class VirusGame:
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

    def start(self):
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
        if self.player_color is not None and self.player_color != self.state["turn"]:
            return

        if self.is_client:
            self.mediator.post(MOVE_REQUESTED, {"row": row, "col": col}, delivery=Delivery.TO_SERVER)
        else:
            self.mediator.post(MOVE_REQUESTED, {"row": row, "col": col}, delivery=Delivery.LOCAL)

    def legal_hints(self):
        return legal_moves(self.state["board"], self.state["turn"])

    def status_caption(self):
        return build_title(
            self.mode,
            self.state,
            player_color=self.player_color,
        )


class VirusRenderer:
    def __init__(self):
        self.screen = None

    def draw(self, screen, state):
        self.screen = screen
        self.screen.fill(BG_COLOR)
        self._draw_board_grid()
        self._draw_legal_hints(state)
        self._draw_pieces(state)
        self._draw_last_move(state)

    def _draw_board_grid(self):
        left = MARGIN
        top = MARGIN
        size = CELL_SIZE * BOARD_SIZE
        right = left + size
        bottom = top + size

        for idx in range(BOARD_SIZE + 1):
            x = left + idx * CELL_SIZE
            y = top + idx * CELL_SIZE
            pygame.draw.line(self.screen, GRID_COLOR, (x, top), (x, bottom), 2)
            pygame.draw.line(self.screen, GRID_COLOR, (left, y), (right, y), 2)

    def _draw_pieces(self, state):
        board = state["board"]
        radius = CELL_SIZE // 3
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                cell = board[row][col]
                if cell == 0:
                    continue
                color = BLACK_COLOR if cell == BLACK else WHITE_COLOR
                pygame.draw.circle(self.screen, color, cell_center(row, col), radius)
                pygame.draw.circle(self.screen, GRID_COLOR, cell_center(row, col), radius, 2)

    def _draw_legal_hints(self, state):
        if state["winner"] is not None:
            return
        radius = CELL_SIZE // 8
        for row, col in legal_moves(state["board"], state["turn"]):
            pygame.draw.circle(self.screen, HINT_COLOR, cell_center(row, col), radius, 2)

    def _draw_last_move(self, state):
        last_move = state["last_move"]
        if last_move is None:
            return
        row, col, _player = last_move
        pygame.draw.circle(self.screen, HINT_COLOR, cell_center(row, col), CELL_SIZE // 2 - 4, 2)


def run_solo():
    pygame.init()
    screen = pygame.display.set_mode((700, 700))
    clock = pygame.time.Clock()

    mediator = UMediator()
    game = VirusGame(mediator, mode="solo")
    renderer = VirusRenderer()
    game.start()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                cell = cell_from_pos(event.pos)
                if cell is not None:
                    row, col = cell
                    game.request_move(row, col)

        mediator.update()
        renderer.draw(screen, game.state)
        pygame.display.set_caption(game.status_caption())
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


def run_client(host: str, port: int, player_color: str, transport_kind: str):
    pygame.init()
    screen = pygame.display.set_mode((700, 700))
    clock = pygame.time.Clock()

    transport = build_transport(transport_kind, "client", host, port)
    mediator = UMediator(transport)
    transport.start_comms(host, port)
    game = VirusGame(mediator, mode="client", player_color=player_color)
    renderer = VirusRenderer()
    game.start()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                cell = cell_from_pos(event.pos)
                if cell is not None:
                    row, col = cell
                    game.request_move(row, col)

        mediator.update()
        renderer.draw(screen, game.state)
        pygame.display.set_caption(game.status_caption())
        pygame.display.flip()
        clock.tick(60)

    transport.shutdown_comms()
    pygame.quit()


def run_server(host: str, port: int, transport_kind: str):
    transport = build_transport(transport_kind, "server", host, port)
    mediator = UMediator(transport)
    transport.start_comms(host, port)
    game = VirusGame(mediator, mode="server")
    game.start()

    try:
        while True:
            mediator.update()
            time.sleep(0.016)
    except KeyboardInterrupt:
        pass
    finally:
        transport.shutdown_comms()


def configure_transport_flags(force_ws: bool):
    if force_ws:
        netlayer_factory.FORCE_WS_TRANSPORT = True
    elif hasattr(netlayer_factory, "FORCE_WS_TRANSPORT"):
        delattr(netlayer_factory, "FORCE_WS_TRANSPORT")


def parse_args():
    parser = argparse.ArgumentParser(description="Tiny umediator v6 POC: le jeu du virus")
    parser.add_argument("--mode", choices=("solo", "server", "client"), default="solo")
    parser.add_argument("--transport", choices=("auto", "socket", "ws"), default="auto")
    parser.add_argument("--force-ws", action="store_true", help="force the engine to select websocket transport")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5005)
    parser.add_argument("--player", choices=(PLAYER_BLACK, PLAYER_WHITE), default=PLAYER_BLACK)
    return parser.parse_args()


def main():
    args = parse_args()
    configure_transport_flags(args.force_ws)
    if args.mode == "solo":
        run_solo()
    elif args.mode == "server":
        run_server(args.host, args.port, args.transport)
    else:
        run_client(args.host, args.port, args.player, args.transport)


if __name__ == "__main__":
    main()
