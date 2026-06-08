---
name: pyved-multiplayer-workflow
description: Use when working on pyved-engine multiplayer game bundles, cartridges, metadata, detached servers, pyv-cli workflow commands, or browser-compatible multiplayer demos.
---

# Pyved Multiplayer Bundle Workflow

This skill captures the project-specific workflow for creating, testing, freezing, and deploying multiplayer games with pyved-engine.

Use it when the task mentions `pyv-cli`, cartridges, bundles, `metadat.json`, `netcode/`, detached servers, multiplayer demos, browser-compatible clients, or freezing/deployment.

## Core Vocabulary

- A cartridge is the game specification folder. It contains `metadat.json`, game Python files such as `gamedef.py`, assets, sounds, declared data files, and optionally `netcode/`.
- A hot cartridge is a development-time cartridge folder. Its structure is similar to a cartridge embedded in a frozen bundle, but it is not wrapped by `launch_game.py`.
- A frozen bundle is a wrapper folder around exactly one cartridge folder plus `launch_game.py`.
- A detached server is a server-only deployment folder generated from a multiplayer cartridge that has server-side logic.

## Canonical Layouts

Hot cartridge:

```text
TheGrid/
  metadat.json
  gamedef.py
  glvars.py
  assets...
  sounds...
  netcode/          required when has_game_server=true
  data files...     paths declared in metadat.json:data_files
```

Frozen bundle:

```text
TheGrid_bundle/     convention only; developers may rename this outer folder
  launch_game.py
  TheGrid/          inner cartridge; folder name must equal metadat.json:slug
    metadat.json    frozen=true
    gamedef.py
    assets...
    sounds...
    netcode/
    data files...
  detached_server/  generated only when has_game_server=true
```

Detached server:

```text
detached_server/
  main.py
  netcode/          copied from TheGrid/netcode
  pyved_engine/     copied engine for standalone server execution
  data files...     copied from metadat.json:data_files
```

Do not copy client assets, sounds, GUI files, or client-only source files into `detached_server/` unless they are explicitly listed in `data_files`.

## Metadata Rules

- `slug` is canonical. In a frozen bundle, the inner cartridge folder must be named exactly like `slug`.
- `frozen=false` means the cartridge is still hot/development-time.
- `frozen=true` is set only in the copied cartridge after it is embedded into a frozen bundle.
- Never mutate the original hot cartridge when freezing.
- The outer frozen bundle name is only a convention, usually `<slug>_bundle`; renaming the outer folder is allowed.
- Renaming the inner cartridge folder of a frozen bundle is forbidden.
- `multiplayer=true` means the game client uses networking.
- `has_game_server=true` means the cartridge must contain `netcode/`, and freezing must populate `detached_server/`.
- `kwargs` can provide default runtime values such as `host`, `port`, `player`, and `mode`.
- `data_files` entries are paths relative to the cartridge root. When generating a detached server, copy those same relative paths into `detached_server/`.

## pyv-cli Command Rules

All cartridge/bundle commands require an explicit target folder name.

Valid:

```text
pyv-cli play TheGrid --host localhost --port 12881 --player 1
pyv-cli serve TheGrid --host localhost --port 12881 --mode ws
pyv-cli freeze TheGrid
pyv-cli test TheGrid
pyv-cli refresh TheGrid
```

Forbidden:

```text
pyv-cli play .
pyv-cli serve .
pyv-cli freeze .
```

The command argument `.` is intentionally unsupported. Do not reintroduce backward compatibility for current-folder execution.

When adding or changing CLI subcommands:

- Update `src/pyvcmdline/cli_spec.py` for parser definitions and help text.
- Update `src/pyvcmdline/__main__.py` only for dispatch behavior.
- Put command behavior in `src/pyvcmdline/subcommand.py`.
- Preserve pass-through extra args for `play` and `serve`.
- Use only `unittest` for dedicated tests.

## Multiplayer Workflow

1. Prototype locally with a hot cartridge.

The developer edits the cartridge folder directly. For multiplayer games with a server, keep `netcode/` inside the cartridge and set `has_game_server=true`.

2. Run the authoritative server locally.

Use:

```text
pyv-cli serve TheGrid --host localhost --port 12881 --mode socket
```

Use websocket mode when testing browser clients or a web-compatible transport.

3. Run one or more clients.

Use:

```text
pyv-cli play TheGrid --host localhost --port 12881 --player 1
pyv-cli play TheGrid --host localhost --port 12881 --player 2
```

Client arguments may also come from `metadat.json:kwargs` when CLI args are not supplied.

4. Test browser-compatible clients against the local server.

Browser-compatible games must follow the pyved canonical callback/template style. Avoid raw infinite loops such as `while True`; these do not translate cleanly to the async browser execution model.

5. Freeze the cartridge into a full bundle.

Use:

```text
pyv-cli freeze TheGrid
```

The frozen output should look like `<slug>_bundle/launch_game.py` plus `<slug>_bundle/<slug>/`.

6. Generate detached server contents when applicable.

If `has_game_server=true`, freezing should populate `detached_server/` with `main.py`, `netcode/`, `pyved_engine/`, and declared `data_files`.

7. Deploy the detached server.

The detached server is intended to be hosted remotely, similarly to a website or service. Browser-based clients connect to this authoritative server. This enables persistence across client reconnects when the server is hosted in the cloud.

## Event System And Transport Notes

- Use event system v6 / `umediator` for the new multiplayer workflow.
- The event system must keep the same concepts for solo and multiplayer games. Solo mode is the default when no transport configuration is supplied.
- Multiplayer architecture is client-server only.
- Only the authoritative server should broadcast to clients.
- Clients send events to the server; clients do not contact other clients directly.
- Transport auto-selection belongs in the engine, not in individual demos.
- Default transport is socket.
- If `FORCE_WS_TRANSPORT` is present in globals, force websocket relay transport.
- If `__BRYTHON__` is present in globals, auto-selection should target a web-compatible websocket layer identified by `WEB_COMPAT_WS`.

## Browser-Compatible Game Structure

When creating a browser-compatible multiplayer example:

- Follow the engine's canonical game definition style, for example `declare_begin`, `declare_update`, and `declare_end`, or the local equivalent already used by the project.
- Do not use raw pygame-style `while True` loops.
- Keep server logic separate from client GUI logic.
- Put authoritative server behavior in `netcode/`.
- Keep browser/client connection configuration in metadata or CLI args.
- Use `examples/TheGrid` as the main reference for a real browser-compatible multiplayer game layout.

## Useful Reference Files

- `examples/TheGrid/metadat.json`
- `examples/TheGrid/gamedef.py`
- `examples/TheGrid/netcode/run_server.py`
- `examples/TheGrid/detached_server/main.py`
- `examples/TheGrid/detached_server/about-detached-server.txt`
- `examples/TheGrid/info-selection-du-serveur.txt`
- `src/pyvcmdline/cli_spec.py`
- `src/pyvcmdline/__main__.py`
- `src/pyvcmdline/subcommand.py`
- `tests/test_pyvcmdline_cli.py`

## Implementation Checks

Before finishing CLI or workflow changes:

- Compile touched Python files with `python -m py_compile`.
- Run focused unit tests with `python -m unittest ...`.
- For CLI command behavior, add or update tests in `tests/test_pyvcmdline_cli.py`.
- Verify examples and help text do not mention `pyv-cli <command> .`.
- Do not revert unrelated user changes in the working tree.
