import os
import json
import shutil
import sys
import tempfile
import types
import unittest


SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from pyvcmdline import __main__ as cli
from pyvcmdline import subcommand


class DummyParser:
    def __init__(self):
        self.help_called = False

    def print_help(self):
        self.help_called = True


class PyvCliTests(unittest.TestCase):
    def test_main_inner_preserves_extra_args_for_play(self):
        calls = []
        original = cli.CMD_MAPPING["play"]

        def fake_play(bundle_name, extra_args=None, **kwargs):
            calls.append((bundle_name, list(extra_args or []), kwargs))

        cli.CMD_MAPPING["play"] = fake_play
        try:
            argns = types.SimpleNamespace(
                subcommand="play",
                version=False,
                help=False,
                bundle_name="MyGame",
                dev=False,
                host="127.0.0.1",
                port=9000,
                player=None,
                mode="socket",
            )
            cli.main_inner(DummyParser(), argns, ["arg0", "arg1"])
        finally:
            cli.CMD_MAPPING["play"] = original

        self.assertEqual(calls, [("MyGame", ["arg0", "arg1"], {"dev": False, "host": "127.0.0.1", "port": 9000, "mode": "socket"})])

    def test_pub_is_disabled_intentionally(self):
        with self.assertRaises(NotImplementedError):
            subcommand.pub("AnyBundle")

    def test_main_inner_rejects_current_folder_target(self):
        argns = types.SimpleNamespace(
            subcommand="play",
            version=False,
            help=False,
            bundle_name=".",
            dev=False,
            host=None,
            port=None,
            player=None,
            mode=None,
        )

        with self.assertRaises(ValueError):
            cli.main_inner(DummyParser(), argns, [])

    def test_freeze_rejects_current_folder_target(self):
        with self.assertRaises(ValueError):
            subcommand.freeze(".")

    def test_freeze_embeds_cartridge_and_populates_detached_server(self):
        original_cwd = os.getcwd()
        original_copy_engine = subcommand._copy_pyved_engine_tree
        temp_dir = tempfile.mkdtemp()

        def fake_copy_engine(target_root):
            os.makedirs(os.path.join(target_root, "pyved_engine"))

        subcommand._copy_pyved_engine_tree = fake_copy_engine
        try:
            os.chdir(temp_dir)
            os.makedirs(os.path.join("TheGrid", "netcode", "shared_code"))
            os.makedirs(os.path.join("TheGrid", "server_state"))

            metadata = {
                "dependencies": [["pyved_engine", "25_4a1", "pyv"]],
                "frozen": False,
                "description": "test",
                "author": "Unknown",
                "asset_base_folder": ".",
                "asset_list": [],
                "sound_base_folder": ".",
                "sound_list": [],
                "data_files": ["server_state/default.json"],
                "slug": "TheGrid",
                "title": "TheGrid",
                "build_date": "before",
                "thumbnail512x512": "thumbnailSQ.png",
                "thumbnail512x384": "thumbnailR.png",
                "ktg_services": False,
                "instructions": "none",
                "uses_challenge": False,
                "has_game_server": True,
                "ncr_faucet": False,
                "multiplayer": True,
                "game_genre": ["Experimental"],
                "source_files": ["gamedef.py", "netcode/run_server.py"],
                "kwargs": {},
            }
            with open(os.path.join("TheGrid", "metadat.json"), "w", encoding="utf-8") as fptr:
                json.dump(metadata, fptr)
            with open(os.path.join("TheGrid", "gamedef.py"), "w", encoding="utf-8") as fptr:
                fptr.write("def init(**kwargs): pass\n")
            with open(os.path.join("TheGrid", "netcode", "run_server.py"), "w", encoding="utf-8") as fptr:
                fptr.write("def exec(**kwargs): pass\n")
            with open(os.path.join("TheGrid", "netcode", "shared_code", "glvars.py"), "w", encoding="utf-8") as fptr:
                fptr.write("pyv = None\n")
            with open(os.path.join("TheGrid", "server_state", "default.json"), "w", encoding="utf-8") as fptr:
                fptr.write("{}")

            subcommand.freeze("TheGrid")

            with open(os.path.join("TheGrid", "metadat.json"), "r", encoding="utf-8") as fptr:
                original_metadata = json.load(fptr)
            with open(os.path.join("TheGrid_bundle", "TheGrid", "metadat.json"), "r", encoding="utf-8") as fptr:
                frozen_metadata = json.load(fptr)

            self.assertFalse(original_metadata["frozen"])
            self.assertTrue(frozen_metadata["frozen"])
            self.assertEqual(frozen_metadata["slug"], "TheGrid")
            self.assertTrue(os.path.isfile(os.path.join("TheGrid_bundle", "launch_game.py")))
            self.assertTrue(os.path.isfile(os.path.join("TheGrid_bundle", "TheGrid", "gamedef.py")))
            self.assertTrue(os.path.isfile(os.path.join("TheGrid_bundle", "detached_server", "main.py")))
            self.assertTrue(os.path.isfile(os.path.join("TheGrid_bundle", "detached_server", "netcode", "run_server.py")))
            self.assertTrue(os.path.isfile(os.path.join("TheGrid_bundle", "detached_server", "server_state", "default.json")))
            self.assertFalse(os.path.exists(os.path.join("TheGrid_bundle", "cartridge")))
        finally:
            subcommand._copy_pyved_engine_tree = original_copy_engine
            os.chdir(original_cwd)
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    unittest.main()
