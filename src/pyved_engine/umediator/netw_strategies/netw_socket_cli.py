import json
import socket
import threading
import time

from ..protocol import ensure_envelope


_mediator = None
_ref_socket = None
_receiver_thread = None
_stop_event = threading.Event()


def get_server_flag():
    return 0


def _receive_updates(host_info, port_info):
    global _ref_socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host_info, port_info))
        _ref_socket = sock
        print("Socket connection established")
        try:
            while not _stop_event.is_set():
                data = sock.recv(4096)
                if not data:
                    break
                envelope = ensure_envelope(json.loads(data.decode()))
                if _mediator is None:
                    print("No mediator registered on socket client")
                else:
                    _mediator.ingest_remote_envelope(envelope)
        except Exception as exc:
            print(f"Socket error: {exc}")
        finally:
            _ref_socket = None
            print("Socket connection closed")


def start_comms(host_info, port_info):
    global _receiver_thread
    _stop_event.clear()
    _receiver_thread = threading.Thread(target=_receive_updates, args=(host_info, port_info))
    _receiver_thread.start()

    timeout = 5
    start_time = time.time()
    while _ref_socket is None and time.time() - start_time < timeout:
        time.sleep(0.1)

    if _ref_socket is None:
        print("Failed to establish socket connection within timeout.")


def send_to_server(envelope):
    global _ref_socket
    if _ref_socket is None:
        print("No active socket connection")
        return
    message = ensure_envelope(envelope).to_json()
    try:
        _ref_socket.sendall(message.encode())
    except Exception as exc:
        print(f"Error sending data: {exc}")


def broadcast_to_clients(envelope):
    raise RuntimeError("client transports cannot broadcast to other clients")


def register_mediator(mediator):
    global _mediator
    _mediator = mediator


def shutdown_comms():
    global _ref_socket, _receiver_thread
    _stop_event.set()
    if _ref_socket is not None:
        try:
            _ref_socket.shutdown(socket.SHUT_RDWR)
        except Exception as exc:
            print(f"Error during socket shutdown: {exc}")
        try:
            _ref_socket.close()
        except Exception as exc:
            print(f"Error closing socket: {exc}")
        _ref_socket = None
    if _receiver_thread is not None:
        _receiver_thread.join()
        _receiver_thread = None
    print("Communication shutdown complete.")

