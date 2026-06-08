import json
import threading

import websocket

from ..protocol import ensure_envelope


_mediator = None
_ref_ws = None
_ws_connected_event = threading.Event()


def get_server_flag():
    return 0


def ws_on_message(ws, message):
    envelope = ensure_envelope(json.loads(message))
    if _mediator is None:
        print("No mediator registered on websocket client")
        return
    _mediator.ingest_remote_envelope(envelope)


def ws_on_error(ws, error):
    print(f"WebSocket error: {error}")


def ws_on_close(ws, close_status_code, close_msg):
    print("WebSocket connection closed")


def ws_on_open(ws):
    global _ref_ws
    _ref_ws = ws
    print("WebSocket connection opened")
    _ws_connected_event.set()


def _run_client(host_info, port_info):
    url = f"ws://{host_info}:{port_info}"
    client_ws = websocket.WebSocketApp(
        url,
        on_message=ws_on_message,
        on_error=ws_on_error,
        on_close=ws_on_close,
        on_open=ws_on_open,
    )
    client_ws.run_forever()


def start_comms(host_info, port_info):
    _ws_connected_event.clear()
    client_thread = threading.Thread(target=_run_client, args=(host_info, port_info))
    client_thread.start()
    print("Waiting for WebSocket connection...")
    _ws_connected_event.wait()
    print("WebSocket connection established and ready.")


def send_to_server(envelope):
    global _ref_ws
    if _ref_ws is None:
        print("No active WebSocket connection")
        return
    message = ensure_envelope(envelope).to_json()
    _ref_ws.send(message)


def broadcast_to_clients(envelope):
    raise RuntimeError("client transports cannot broadcast to other clients")


def register_mediator(mediator):
    global _mediator
    _mediator = mediator


def shutdown_comms():
    global _ref_ws
    if _ref_ws:
        _ref_ws.close()
        _ref_ws = None
