import os
import sys
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


if __name__ == "__main__":
    unittest.main()
