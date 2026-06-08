from __future__ import annotations

import textwrap


GLOBAL_HELP = {
    "usage": "pyv-cli [option] subcommand [subcommand_options]",
    "description": "Command line tool for pyved-engine, used to operate with/manipulate game bundles.",
    "epilog": textwrap.dedent("""\
        Tips:
          • Run `pyv-cli <subcommand> -h` for detailed help and examples of that subcommand.
          • Use `-d/--dev` with `share` to target the developer sandbox.

        Examples:
          pyv-cli init MyNewGame
          pyv-cli play . --host 127.0.0.1 --port 8765 --mode ws
          pyv-cli serve MyServerBundle --host 0.0.0.0 --port 9000
          pyv-cli refresh .
          pyv-cli upgrade MyGame
    """),
}


COMMAND_SECTIONS = (
    ("workflow", "Core workflow", ("init", "play", "serve", "upgrade", "freeze")),
    ("utility", "Utility and maintenance", ("refresh", "bump", "test", "ts-creation")),
    ("distribution", "Publishing and sharing", ("share", "pub")),
    ("developer", "Developer tools", ("autogen",)),
)


COMMAND_SPECS = {
    "init": {
        "help": "initialize a new game bundle",
        "description": textwrap.dedent("""\
            Initialize a new game bundle.

            Creates the basic folder structure and metadata to start a project.
        """),
        "epilog": textwrap.dedent("""\
            Examples:
              pyv-cli init MyNewGame
              pyv-cli init mygame
        """),
        "args": [
            {"name": "bundle_name", "kwargs": {"type": str, "help": "Name of the bundle"}},
        ],
    },
    "play": {
        "help": "play a given game bundle in the local context",
        "description": textwrap.dedent("""\
            Run a bundle locally (client-side).

            Useful for quick iteration when developing gameplay.
        """),
        "epilog": textwrap.dedent("""\
            Examples:
              pyv-cli play .
              pyv-cli play MyGame --mode ws
              pyv-cli play MyGame --host 127.0.0.1 --port 8765 --player 2
        """),
        "args": [
            {"name": "bundle_name", "kwargs": {"type": str, "nargs": "?", "default": ".", "help": "Specified bundle (default: current folder)"}},
            {"name": "--host", "kwargs": {"type": str, "help": "Server hostname"}},
            {"name": "--port", "kwargs": {"type": int, "help": "Server port"}},
            {"name": "--player", "kwargs": {"type": int, "help": "local player identifier"}},
            {"name": "--mode", "kwargs": {"type": str, "help": "what type of transport layer to use (ws/socket/etc)"}},
        ],
    },
    "autogen": {
        "help": "for system devs only (=dev tool equivalent to a PyConnector autogen script)",
        "description": "Developer-only tool. Generates code/assets from internal templates.",
        "epilog": None,
        "args": [],
    },
    "upgrade": {
        "help": "upgrade a game to enable katagames API calls",
        "description": textwrap.dedent("""\
            Upgrade a bundle to enable Katagames/pyved integrations.

            Typical tasks may include:
              • adding or updating integration hooks
              • adjusting bundle metadata
              • preparing files for API calls

            (Exact actions depend on the pyv-cli version you're using)
        """),
        "epilog": textwrap.dedent("""\
            Usage:
              pyv-cli upgrade <bundle_name>

            Examples:
              pyv-cli upgrade .
              pyv-cli upgrade MyGame
        """),
        "args": [
            {"name": "bundle_name", "kwargs": {"type": str, "help": "Specified bundle"}},
        ],
    },
    "freeze": {
        "help": "freeze a hot bundle into a standalone cartridge layout",
        "description": textwrap.dedent("""\
            Freeze a bundle into a more distributable folder layout.

            The command currently creates a frozen copy of the bundle with a launcher
            and a cartridge folder, and starts preparing the detached-server layout
            for multiplayer bundles.
        """),
        "epilog": textwrap.dedent("""\
            Examples:
              pyv-cli freeze .
              pyv-cli freeze MyGame
        """),
        "args": [
            {"name": "bundle_name", "kwargs": {"type": str, "help": "Specified bundle"}},
        ],
    },
    "refresh": {
        "help": "rescan source/assets and update bundle metadata",
        "description": textwrap.dedent("""\
            Refresh the bundle metadata by scanning source files and assets.

            Useful after adding/removing files so metadata stays in sync.
        """),
        "epilog": textwrap.dedent("""\
            Examples:
              pyv-cli refresh .
              pyv-cli refresh MyGame
        """),
        "args": [
            {"name": "bundle_name", "kwargs": {"type": str}},
        ],
    },
    "bump": {
        "help": "update bundle metadata to mark current pyved-engine revision",
        "description": textwrap.dedent("""\
            Bump the engine revision used by the bundle.

            Records that the bundle targets the current pyved-engine version.
        """),
        "epilog": textwrap.dedent("""\
            Examples:
              pyv-cli bump .
              pyv-cli bump MyGame
        """),
        "args": [
            {"name": "bundle_name", "kwargs": {"type": str}},
        ],
    },
    "serve": {
        "help": "run the server code for a given game bundle",
        "description": textwrap.dedent("""\
            Start the server side for a bundle.

            Forwarded options let you bind host/port and select transport.
        """),
        "epilog": textwrap.dedent("""\
            Examples:
              pyv-cli serve MyServerBundle
              pyv-cli serve MyServerBundle --host 0.0.0.0 --port 9000
              pyv-cli serve . --mode ws
        """),
        "args": [
            {"name": "bundle_name", "kwargs": {"type": str, "help": "Specified bundle (default: current folder)"}},
            {"name": "--host", "kwargs": {"type": str, "help": "Server hostname"}},
            {"name": "--port", "kwargs": {"type": int, "help": "Server port"}},
            {"name": "--player", "kwargs": {"type": int, "help": "local player identifier"}},
            {"name": "--mode", "kwargs": {"type": str, "help": "what type of transport layer to use (ws/socket/etc)"}},
        ],
    },
    "share": {
        "help": "share a given game bundle with the world",
        "description": textwrap.dedent("""\
            Share a bundle (publish or make it accessible as configured).

            Notes:
              • This subcommand accepts the global --dev flag to target the developer server.
        """),
        "epilog": textwrap.dedent("""\
            Examples:
              pyv-cli share .
              pyv-cli --dev share MyGame
        """),
        "args": [
            {"name": "bundle_name", "kwargs": {"type": str, "nargs": "?", "default": ".", "help": "Specified bundle (default: current folder)"}},
        ],
    },
    "test": {
        "help": "validate that a bundle is structurally correct",
        "description": textwrap.dedent("""\
            Run validation checks on a bundle.

            Verifies structure and basic expectations so you can catch issues early.
        """),
        "epilog": textwrap.dedent("""\
            Examples:
              pyv-cli test .
              pyv-cli test MyGame
        """),
        "args": [
            {"name": "bundle_name", "kwargs": {"type": str}},
        ],
    },
    "ts-creation": {
        "help": "create the JSON file that matches a tileset",
        "description": textwrap.dedent("""\
            Create a tileset JSON from a source image.

            Generates a JSON description that matches your tileset sheet.
        """),
        "epilog": textwrap.dedent("""\
            Example:
              pyv-cli ts-creation assets/tileset.png
        """),
        "args": [
            {"name": "image_path", "kwargs": {"type": str}},
        ],
    },
    "pub": {
        "help": "request game publication given a sandboxed-share slug",
        "description": textwrap.dedent("""\
            Request publication for an existing game slug (cloud-based storage).

            This assumes the game has already been shared/synced to the sandbox.
        """),
        "epilog": textwrap.dedent("""\
            Example:
              pyv-cli pub my-game-slug
        """),
        "args": [
            {"name": "slug", "kwargs": {"type": str, "help": "existing game slug (=identifier in the cloud-based storage)"}},
        ],
    },
}


def command_names():
    return tuple(COMMAND_SPECS.keys())


def workflow_commands():
    return COMMAND_SECTIONS[0][2]


def utility_commands():
    return COMMAND_SECTIONS[1][2]


def is_known_command(name):
    return name in COMMAND_SPECS
