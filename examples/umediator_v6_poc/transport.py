from __future__ import annotations

import asyncio
import json
import socket
import threading
import time

import websockets

from pyved_engine.umediator.protocol import ensure_envelope
from pyved_engine.umediator.netlayer_factory import resolve_transport_code


class SocketRelayTransport:
    def __init__(self, role: str, host: str, port: int):
        if role not in {"server", "client"}:
            raise ValueError("role must be 'server' or 'client'")

        self._role = role
        self._host = host
        self._port = port
        self._mediator = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._server_socket = None
        self._server_clients = []
        self._server_threads = []
        self._client_socket = None
        self._client_thread = None

    def get_server_flag(self):
        return 1 if self._role == "server" else 0

    def register_mediator(self, mediator):
        self._mediator = mediator

    def _log(self, message):
        print(f"[socket {self._role}] {message}")

    def _deliver_envelope(self, raw_payload: str):
        if not raw_payload.strip():
            return
        envelope = ensure_envelope(json.loads(raw_payload))
        if self._mediator is not None:
            self._mediator.ingest_remote_envelope(envelope)

    def _socket_reader(self, sock: socket.socket):
        buffer = ""
        sock.settimeout(0.5)
        peer = None
        try:
            peer = sock.getpeername()
        except OSError:
            pass
        while not self._stop_event.is_set():
            try:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode("utf-8")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self._deliver_envelope(line)
            except socket.timeout:
                continue
            except OSError:
                break
        if peer is not None and self._role == "server":
            self._log(f"connection closed by {peer[0]}:{peer[1]}")
        elif self._role == "server":
            self._log("connection closed")

    def start_comms(self, host_info, port_info):
        self._host = host_info
        self._port = port_info
        self._stop_event.clear()

        if self._role == "server":
            self._start_server()
        else:
            self._start_client()

    def _start_server(self):
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((self._host, self._port))
        self._server_socket.listen()
        self._server_socket.settimeout(0.5)
        self._log(f"listening on {self._host}:{self._port}")

        def accept_loop():
            while not self._stop_event.is_set():
                try:
                    client_sock, _ = self._server_socket.accept()
                    peer = client_sock.getpeername()
                    self._log(f"new connection from {peer[0]}:{peer[1]}")
                    with self._lock:
                        self._server_clients.append(client_sock)
                    reader = threading.Thread(target=self._socket_reader, args=(client_sock,), daemon=True)
                    reader.start()
                    self._server_threads.append(reader)
                except socket.timeout:
                    continue
                except OSError:
                    break

        thread = threading.Thread(target=accept_loop, daemon=True)
        thread.start()
        self._server_threads.append(thread)

    def _start_client(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        deadline = time.time() + 5.0
        while True:
            try:
                sock.connect((self._host, self._port))
                break
            except OSError:
                if time.time() >= deadline:
                    raise
                time.sleep(0.1)
        self._client_socket = sock
        self._client_thread = threading.Thread(target=self._socket_reader, args=(sock,), daemon=True)
        self._client_thread.start()
        self._log(f"connected to {self._host}:{self._port}")

    def _send_line(self, sock: socket.socket, envelope):
        message = ensure_envelope(envelope).to_json() + "\n"
        sock.sendall(message.encode("utf-8"))

    def send_to_server(self, envelope):
        if self._role != "client":
            raise RuntimeError("server transport cannot send events to a server")
        if self._client_socket is None:
            raise RuntimeError("no active client socket")
        self._send_line(self._client_socket, envelope)

    def broadcast_to_clients(self, envelope):
        if self._role != "server":
            raise RuntimeError("client transports cannot broadcast to other clients")

        broken = []
        with self._lock:
            clients = list(self._server_clients)
        for client_sock in clients:
            try:
                self._send_line(client_sock, envelope)
            except OSError:
                broken.append(client_sock)

        if broken:
            with self._lock:
                for client_sock in broken:
                    try:
                        self._server_clients.remove(client_sock)
                    except ValueError:
                        pass
                    try:
                        client_sock.close()
                    except OSError:
                        pass

    def shutdown_comms(self):
        self._stop_event.set()

        if self._client_socket is not None:
            try:
                self._client_socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                self._client_socket.close()
            except OSError:
                pass
            self._client_socket = None

        with self._lock:
            clients = list(self._server_clients)
            self._server_clients.clear()
        for client_sock in clients:
            try:
                client_sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                client_sock.close()
            except OSError:
                pass

        if self._server_socket is not None:
            try:
                self._server_socket.close()
            except OSError:
                pass
            self._server_socket = None

        for thread in list(self._server_threads):
            if thread.is_alive():
                thread.join(timeout=0.5)
        self._server_threads.clear()

        if self._client_thread is not None and self._client_thread.is_alive():
            self._client_thread.join(timeout=0.5)
        self._client_thread = None
        self._log("communication shutdown complete")


class WebSocketRelayTransport:
    def __init__(self, role: str, host: str, port: int):
        if role not in {"server", "client"}:
            raise ValueError("role must be 'server' or 'client'")

        self._role = role
        self._host = host
        self._port = port
        self._mediator = None
        self._server_loop = None
        self._server_thread = None
        self._server_stop = None
        self._server_ready = threading.Event()
        self._server_connections = set()
        self._server_connections_lock = threading.Lock()
        self._client_loop = None
        self._client_thread = None
        self._client_ws = None
        self._client_ready = threading.Event()

    def get_server_flag(self):
        return 1 if self._role == "server" else 0

    def register_mediator(self, mediator):
        self._mediator = mediator

    def _log(self, message):
        print(f"[ws {self._role}] {message}")

    def _deliver_envelope(self, raw_payload: str):
        envelope = ensure_envelope(json.loads(raw_payload))
        if self._mediator is not None:
            self._mediator.ingest_remote_envelope(envelope)

    async def _server_client_handler(self, ws_obj):
        with self._server_connections_lock:
            self._server_connections.add(ws_obj)
        remote = getattr(ws_obj, "remote_address", None)
        if remote:
            self._log(f"new connection from {remote[0]}:{remote[1]}")
        else:
            self._log("new connection")
        try:
            async for message in ws_obj:
                self._deliver_envelope(message)
        finally:
            with self._server_connections_lock:
                self._server_connections.discard(ws_obj)
            if remote:
                self._log(f"connection closed by {remote[0]}:{remote[1]}")
            else:
                self._log("connection closed")

    async def _server_main(self):
        self._server_stop = asyncio.Event()
        async with websockets.serve(self._server_client_handler, self._host, self._port):
            self._server_ready.set()
            self._log(f"listening on ws://{self._host}:{self._port}")
            await self._server_stop.wait()

    def _run_server_loop(self):
        self._server_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._server_loop)
        try:
            self._server_loop.run_until_complete(self._server_main())
        finally:
            pending = asyncio.all_tasks(self._server_loop)
            for task in pending:
                task.cancel()
            if pending:
                self._server_loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            self._server_loop.close()

    async def _client_main(self):
        url = f"ws://{self._host}:{self._port}"
        async with websockets.connect(url) as ws_obj:
            self._client_ws = ws_obj
            self._client_ready.set()
            self._log(f"connected to {url}")
            try:
                async for message in ws_obj:
                    self._deliver_envelope(message)
            finally:
                self._client_ws = None
                self._log("connection closed")

    def _run_client_loop(self):
        self._client_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._client_loop)
        try:
            self._client_loop.run_until_complete(self._client_main())
        finally:
            pending = asyncio.all_tasks(self._client_loop)
            for task in pending:
                task.cancel()
            if pending:
                self._client_loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            self._client_loop.close()

    def start_comms(self, host_info, port_info):
        self._host = host_info
        self._port = port_info

        if self._role == "server":
            self._server_ready.clear()
            self._server_thread = threading.Thread(target=self._run_server_loop, daemon=True)
            self._server_thread.start()
            if not self._server_ready.wait(timeout=5.0):
                raise TimeoutError("websocket server did not become ready in time")
        else:
            self._client_ready.clear()
            self._client_thread = threading.Thread(target=self._run_client_loop, daemon=True)
            self._client_thread.start()
            if not self._client_ready.wait(timeout=5.0):
                raise TimeoutError("websocket client did not connect in time")

    def send_to_server(self, envelope):
        if self._role != "client":
            raise RuntimeError("server transport cannot send events to a server")
        if self._client_loop is None or self._client_ws is None:
            raise RuntimeError("no active websocket connection")
        future = asyncio.run_coroutine_threadsafe(
            self._client_ws.send(ensure_envelope(envelope).to_json()),
            self._client_loop,
        )
        future.result()

    async def _broadcast_async(self, envelope):
        message = ensure_envelope(envelope).to_json()
        with self._server_connections_lock:
            connections = list(self._server_connections)
        broken = []
        for ws_obj in connections:
            try:
                await ws_obj.send(message)
            except Exception:
                broken.append(ws_obj)
        if broken:
            with self._server_connections_lock:
                for ws_obj in broken:
                    self._server_connections.discard(ws_obj)

    def broadcast_to_clients(self, envelope):
        if self._role != "server":
            raise RuntimeError("client transports cannot broadcast to other clients")
        if self._server_loop is None or not self._server_loop.is_running():
            raise RuntimeError("websocket server is not running")
        future = asyncio.run_coroutine_threadsafe(self._broadcast_async(envelope), self._server_loop)
        future.result()

    def shutdown_comms(self):
        if self._role == "server":
            if self._server_loop is not None and self._server_stop is not None:
                self._server_loop.call_soon_threadsafe(self._server_stop.set)
            if self._server_thread is not None and self._server_thread.is_alive():
                self._server_thread.join(timeout=1.0)
            self._server_thread = None
            self._server_loop = None
            self._server_stop = None
            self._server_ready.clear()
            with self._server_connections_lock:
                self._server_connections.clear()
            self._log("communication shutdown complete")
        else:
            if self._client_loop is not None and self._client_ws is not None:
                try:
                    future = asyncio.run_coroutine_threadsafe(self._client_ws.close(), self._client_loop)
                    future.result(timeout=1.0)
                except Exception:
                    pass
            if self._client_thread is not None and self._client_thread.is_alive():
                self._client_thread.join(timeout=1.0)
            self._client_thread = None
            self._client_loop = None
            self._client_ws = None
            self._client_ready.clear()
            self._log("communication shutdown complete")


def build_transport(transport_kind: str, role: str, host: str, port: int):
    resolved_kind = resolve_transport_code(transport_kind)
    if resolved_kind == "SOCKET":
        return SocketRelayTransport(role, host, port)
    if resolved_kind in {"WS", "WEB_SOCKET_RELAY", "WEB_COMPAT_WS"}:
        return WebSocketRelayTransport(role, host, port)
    raise ValueError("transport_kind must resolve to a socket or websocket transport")
