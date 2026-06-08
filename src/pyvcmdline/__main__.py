# pyvcmdline/__main__.py
"""
Command line interface for pyved-engine.
"""
import argparse
from . import subcommand
from .cli_spec import COMMAND_SPECS, GLOBAL_HELP, is_known_command
from .pyvcli_defs import VER_DISP_MSG
from .pyvcli_defs import pe_vars

__version__ = pe_vars.ENGINE_VERSION_STR

HELP = {"global": GLOBAL_HELP}

CMD_MAPPING = {
    "autogen": None,
    "bump": subcommand.bump,
    "init": subcommand.init,
    "freeze": subcommand.freeze,
    "play": subcommand.play,
    "serve": subcommand.serve,
    "pub": subcommand.pub,
    "refresh": subcommand.refresh,
    "share": subcommand.share,
    "test": subcommand.test,
    "ts-creation": subcommand.ts_creation,
    "upgrade": subcommand.upgrade,
}

# Unified formatter (keeps newlines, shows defaults)
class SmartFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass


# TODO the deprecated code below may be useful to implementing a future "repair" bundle subcommand
# def _bundle_renaming(path_to_bundle):
#     # ensure that OUR NORM is respected:
#     # what norm? We need to enforce the rule that states:
#     # the directory name == the slug
#     pass


def trigger_publish(slug):  # deprecated func
    """
    once the game is available server-side, as a stored cartridge,
    (therefore your game has a slug/Server-side game identifier)

    we trigger the "PUBLISH" op server-side.
    This means the game will spawn/pop within the gaming CMS (cloudarcade)

    :param slug: str that the server uses to uniquely identify a cartridge
    stored server-side
    :return: True/False
    """
    raise NotImplementedError


def _normalize_target_name(x):
    """Trim trailing slashes and reject current-folder targeting."""
    t = x.rstrip('/')
    t = t.rstrip('\\')
    if t in ('', '.'):
        raise ValueError('pyv-cli requires an explicit cartridge/bundle folder name; "." is not supported')
    return t


def _add_subcommand_parser(subparsers, command_name):
    spec = COMMAND_SPECS[command_name]
    parser = subparsers.add_parser(
        command_name,
        help=spec["help"],
        formatter_class=SmartFormatter,
        description=spec["description"],
        epilog=spec["epilog"],
    )
    for arg_spec in spec["args"]:
        parser.add_argument(arg_spec["name"], **arg_spec["kwargs"])
    return parser


def main_inner(parser, argns, extra_args=None):
    """Dispatch selected subcommand."""
    ope_name = argns.subcommand
    extra_args = extra_args or []

    if argns.version:
        print(VER_DISP_MSG % __version__)
        return 0
    if argns.help:
        parser.print_help()
        return 0
    if not is_known_command(ope_name):
        parser.print_help()
        return 1
    if CMD_MAPPING[ope_name] is None:
        raise NotImplementedError(f"subcommand \"{ope_name}\" is valid, but isnt implemented yet!")

    adhoc_subcommand_func = CMD_MAPPING[ope_name]

    if ope_name == "autogen":
        adhoc_subcommand_func()
    elif ope_name in ("play", "serve"):
        kwargs = {
            k: v for k, v in vars(argns).items()
            if k not in ["bundle_name", "command", "subcommand", "version", "help"] and v is not None
        }
        xarg = _normalize_target_name(argns.bundle_name)
        adhoc_subcommand_func(xarg, extra_args=extra_args, **kwargs)
    elif ope_name == "ts-creation":
        adhoc_subcommand_func(argns.image_path)
    elif ope_name == "pub":
        adhoc_subcommand_func(argns.slug)
    else:
        xarg = _normalize_target_name(argns.bundle_name)
        if ope_name == "share":
            adhoc_subcommand_func(xarg, argns.dev)
        else:
            adhoc_subcommand_func(xarg)
    return 0


def do_parse_args():
    """Build CLI and parse arguments."""
    parser = argparse.ArgumentParser(
        description=HELP["global"]["description"],
        add_help=False,
        usage=HELP["global"]["usage"],
        formatter_class=SmartFormatter,
        epilog=HELP["global"]["epilog"]
    )

    # Global options (mutually exclusive to preserve retro-compatibility)
    special_modes_group = parser.add_argument_group('Options')
    either_one_option = special_modes_group.add_mutually_exclusive_group()
    either_one_option.add_argument('-v', '--version', action='store_true', help='Print the current pyved engine version.')
    either_one_option.add_argument('-h', '--help', action='store_true', help='Print this help.')
    either_one_option.add_argument('-d', '--dev', action='store_true', help='Use the developer server (tool debug etc)')

    # Subcommands group
    subparsers = parser.add_subparsers(title="Subcommands", dest="subcommand", required=False, metavar="subcommand")

    for command_name in COMMAND_SPECS:
        _add_subcommand_parser(subparsers, command_name)

    ret_args, extra_args = parser.parse_known_args()
    main_inner(parser, ret_args, extra_args)


if __name__ == '__main__':
    do_parse_args()
