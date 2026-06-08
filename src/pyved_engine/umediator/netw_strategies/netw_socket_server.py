import json
import socket
import threading
import time

from ..protocol import ensure_envelope


_mediator = None
_inbound_connections = []
_ref_threads = []
_socket_ref = None
_shutdown_flag = False


def get_server_flag():
    return 1


def _receive_message(raw_txt):
    envelope = ensure_envelope(json.loads(raw_txt))
    if _mediator is None:
        print("No mediator registered on socket server")
        return
    _mediator.ingest_remote_envelope(envelope)


def start_comms(host_info, port_info):
    global _ref_threads, _socket_ref, _shutdown_flag
    _shutdown_flag = False
    _inbound_connections.clear()
    _ref_threads.clear()

    def handle_client(socklisten):
        global _inbound_connections

        while not _shutdown_flag:
            try:
                conn, addr = socklisten.accept()
                _inbound_connections.append(conn)
                print(f"Connection added, source:{addr}")
                with conn:
                    while not _shutdown_flag:
                        data = conn.recv(4096)
                        if not data:
                            break
                        _receive_message(data.decode())
            except socket.timeout:
                time.sleep(0.1)
            except Exception as exc:
                print(f"Error handling client: {exc}")
                break

    _socket_ref = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _socket_ref.bind((host_info, port_info))
    print("start to listen on:", host_info, port_info)
    _socket_ref.listen()
    _socket_ref.settimeout(1)

    for _ in range(2):
        nt = threading.Thread(target=handle_client, args=(_socket_ref,))
        nt.start()
        _ref_threads.append(nt)


def send_to_server(envelope):
    raise RuntimeError("server transport cannot send events to a server")


def broadcast_to_clients(envelope):
    if _mediator is None:
        print("No mediator registered on socket server")
        return

    message = ensure_envelope(envelope).to_json()
    broken_connections = set()
    for client in list(_inbound_connections):
        try:
            client.sendall(message.encode())
        except Exception as err:
            print("!!connection err!!", err)
            broken_connections.add(client)

    for conn in broken_connections:
        try:
            _inbound_connections.remove(conn)
        except ValueError:
            pass


def register_mediator(mediator):
    global _mediator
    _mediator = mediator


def shutdown_comms():
    global _inbound_connections, _ref_threads, _shutdown_flag, _socket_ref

    _shutdown_flag = True

    for conn in list(_inbound_connections):
        try:
            conn.close()
        except Exception as err:
            print(f"Error closing connection {conn}: {err}")
    _inbound_connections.clear()

    for thread in list(_ref_threads):
        try:
            thread.join()
        except Exception as err:
            print(f"Error stopping thread {thread}: {err}")
    _ref_threads.clear()

    if _socket_ref is not None:
        try:
            _socket_ref.close()
        except Exception as err:
            print(f"Error closing socket: {err}")
        _socket_ref = None
