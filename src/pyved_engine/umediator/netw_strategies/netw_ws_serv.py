import asyncio
import json
import threading

import websockets

from ..protocol import ensure_envelope


_connections = set()
_mediator = None
_loop = None
_executor_tasks = []


def get_server_flag():
    return 1


async def _receive_message(message):
    envelope = ensure_envelope(json.loads(message))
    if _mediator is None:
        print("No mediator registered on websocket server")
        return
    _mediator.ingest_remote_envelope(envelope)


async def _handle_client(ws_obj):
    _connections.add(ws_obj)
    print(f"New connection from {ws_obj.remote_address}")
    try:
        async for message in ws_obj:
            await _receive_message(message)
    except websockets.exceptions.ConnectionClosed as exc:
        print(f"Connection closed: {ws_obj.remote_address} ({exc})")
    finally:
        _connections.discard(ws_obj)
        print("A connection has dropped")


async def _server_start(host_info, port_info):
    async with websockets.serve(_handle_client, host_info, port_info):
        print(f"WebSocket server started on ws://{host_info}:{port_info}")
        await asyncio.Future()


def start_comms(host_i, port_i):
    global _loop
    _loop = asyncio.new_event_loop()

    def _runner():
        asyncio.set_event_loop(_loop)
        _loop.run_until_complete(_server_start(host_i, port_i))

    thread = threading.Thread(target=_runner, daemon=True)
    thread.start()
    _executor_tasks.append(thread)


async def _async_broadcast(event_envelope):
    message = ensure_envelope(event_envelope).to_json()
    broken_connections = set()
    for ws in list(_connections):
        try:
            await ws.send(message)
        except Exception as err:
            print("!! Connection error !!", err)
            broken_connections.add(ws)
    for ws in broken_connections:
        _connections.discard(ws)


def send_to_server(envelope):
    raise RuntimeError("server transport cannot send events to a server")


def broadcast_to_clients(envelope):
    if _loop is not None and _loop.is_running():
        future = asyncio.run_coroutine_threadsafe(_async_broadcast(envelope), _loop)
        future.result()
    else:
        asyncio.run(_async_broadcast(envelope))


def register_mediator(mediator):
    global _mediator
    _mediator = mediator


async def _stop_server():
    for ws in list(_connections):
        try:
            await ws.close()
        except Exception as exc:
            print(f"Error closing connection from {ws.remote_address}: {exc}")


def shutdown_comms():
    global _loop
    if _loop is None:
        return
    _loop.create_task(_stop_server())
    _loop.run_until_complete(_loop.shutdown_asyncgens())
    _loop.stop()
