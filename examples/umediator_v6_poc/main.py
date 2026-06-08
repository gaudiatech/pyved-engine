from __future__ import annotations

import argparse
import sys


def parse_args():
    parser = argparse.ArgumentParser(description="Tiny umediator v6 POC dispatcher")
    parser.add_argument("--mode", choices=("solo", "client", "server"), default="solo")
    return parser.parse_known_args()[0]


def main():
    args = parse_args()
    if args.mode == "server":
        from server import main as server_main

        server_main()
    else:
        from game import main as game_main

        game_main()


if __name__ == "__main__":
    main()
