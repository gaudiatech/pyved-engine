# umediator v6 POC: `le jeu du virus`

This folder contains a tiny runnable proof of concept for the cleaned `umediator` v6 API.

The demo implements the French board game often called `le jeu du virus`:
- 2 players
- a square grid
- each move places a piece on an empty square adjacent to one of your pieces
- after placing, adjacent opponent pieces are converted
- the server is authoritative in multiplayer mode

The POC is intentionally minimal:
- graphics only use `pygame.draw.line` and `pygame.draw.circle`
- no sprite sheets
- no text rendering inside the board
- no extra engine layers

## Run

Solo mode is the default. It uses the mediator with no network layer attached, so it behaves like a local/serverless game.
For multiplayer, `--transport auto` is the default and follows the engine's own selection rules.
By default, the engine resolves `auto` to the native socket transport.

```bash
python examples/umediator_v6_poc/main.py
```

Multiplayer mode uses the same game code, but attaches a socket transport.
You can also switch the backend explicitly with `--transport socket` or `--transport ws`.
If you pass `--force-ws`, the demo sets `FORCE_WS_TRANSPORT` in the engine factory and websocket transport is forced.

Start the server first:

```bash
python examples/umediator_v6_poc/main.py --mode server --host 127.0.0.1 --port 5005
python examples/umediator_v6_poc/main.py --mode server --transport ws --host 127.0.0.1 --port 5005
python examples/umediator_v6_poc/main.py --mode server --transport auto --host 127.0.0.1 --port 5005
python examples/umediator_v6_poc/main.py --mode server --force-ws --host 127.0.0.1 --port 5005
```

Then start one client per human player:

```bash
python examples/umediator_v6_poc/main.py --mode client --player black --host 127.0.0.1 --port 5005
python examples/umediator_v6_poc/main.py --mode client --player white --host 127.0.0.1 --port 5005
python examples/umediator_v6_poc/main.py --mode client --transport ws --player black --host 127.0.0.1 --port 5005
python examples/umediator_v6_poc/main.py --mode client --transport ws --player white --host 127.0.0.1 --port 5005
python examples/umediator_v6_poc/main.py --mode client --transport auto --player black --host 127.0.0.1 --port 5005
python examples/umediator_v6_poc/main.py --mode client --transport auto --player white --host 127.0.0.1 --port 5005
python examples/umediator_v6_poc/main.py --mode client --force-ws --player black --host 127.0.0.1 --port 5005
python examples/umediator_v6_poc/main.py --mode client --force-ws --player white --host 127.0.0.1 --port 5005
```

## Controls

- Left click a legal cell to play
- `Esc` quits the GUI

## Notes

- In solo mode, the exact same mediator machinery works without any transport object.
- In multiplayer mode, only the server broadcasts state updates.
- The clients only send move requests to the server.
- `socket` and `ws` are interchangeable at the demo level because they expose the same mediator transport contract.
