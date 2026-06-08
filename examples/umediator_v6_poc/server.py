from __future__ import annotations

import argparse
import sys
import threading
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
THIS_DIR = Path(__file__).resolve().parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))


from pyved_engine.umediator import UMediator

from runtime import configure_transport_flags
from transport import build_transport


def run_server(host: str, port: int, transport_kind: str):
    transport = build_transport(transport_kind, "server", host, port)
    mediator = UMediator(transport)
    transport.start_comms(host, port)
    print(f"[server] running on {host}:{port} using {transport_kind}")
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        pass
    finally:
        transport.shutdown_comms()


def parse_args():
    parser = argparse.ArgumentParser(description="Tiny umediator v6 POC server")
    parser.add_argument("--transport", choices=("auto", "socket", "ws"), default="auto")
    parser.add_argument("--force-ws", action="store_true", help="force the engine to select websocket transport")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5005)
    return parser.parse_args()


def main():
    args = parse_args()
    configure_transport_flags(args.force_ws)
    run_server(args.host, args.port, args.transport)


if __name__ == "__main__":
    main()
