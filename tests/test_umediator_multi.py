import os
import sys
import unittest


SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from pyved_engine.umediator import Delivery, EventEnvelope, UMediator


class FakeClientTransport:
    def __init__(self):
        self.registered = None
        self.sent = []

    def get_server_flag(self):
        return 0

    def start_comms(self, host_info, port_info):
        return None

    def send_to_server(self, envelope):
        self.sent.append(envelope)

    def broadcast_to_clients(self, envelope):
        raise AssertionError("client transport must not broadcast")

    def register_mediator(self, ref_mediator):
        self.registered = ref_mediator

    def shutdown_comms(self):
        return None


class FakeServerTransport:
    def __init__(self):
        self.registered = None
        self.sent = []
        self.broadcasts = []

    def get_server_flag(self):
        return 1

    def start_comms(self, host_info, port_info):
        return None

    def send_to_server(self, envelope):
        self.sent.append(envelope)
        raise AssertionError("server transport must not send to server")

    def broadcast_to_clients(self, envelope):
        self.broadcasts.append(envelope)

    def register_mediator(self, ref_mediator):
        self.registered = ref_mediator

    def shutdown_comms(self):
        return None


class MediatorMultiTests(unittest.TestCase):
    def test_client_to_server_event_is_forwarded_not_locally_dispatched(self):
        transport = FakeClientTransport()
        mediator = UMediator(transport)
        received = []
        mediator.register("move", received.append)

        mediator.post("move", {"dx": 3}, delivery=Delivery.TO_SERVER)
        mediator.update()

        self.assertEqual(received, [])
        self.assertEqual(len(transport.sent), 1)
        self.assertEqual(transport.sent[0].delivery, Delivery.TO_SERVER)
        self.assertEqual(transport.sent[0].payload, {"dx": 3})

    def test_server_broadcasts_to_clients_and_notifies_locally(self):
        transport = FakeServerTransport()
        mediator = UMediator(transport)
        received = []
        mediator.register("sync", received.append)

        mediator.post("sync", {"tick": 7}, delivery=Delivery.BROADCAST)
        mediator.update()

        self.assertEqual(len(received), 1)
        self.assertEqual(received[0].delivery, Delivery.BROADCAST)
        self.assertEqual(received[0].payload, {"tick": 7})
        self.assertEqual(len(transport.broadcasts), 1)
        self.assertEqual(transport.broadcasts[0].delivery, Delivery.BROADCAST)

    def test_remote_broadcast_received_by_client_stays_local(self):
        transport = FakeClientTransport()
        mediator = UMediator(transport)
        received = []
        mediator.register("state_sync", received.append)

        mediator.ingest_remote_envelope(
            EventEnvelope(
                name="state_sync",
                payload={"hp": 99},
                delivery=Delivery.BROADCAST,
                origin="server",
                event_id="evt-remote",
            )
        )
        mediator.update()

        self.assertEqual(len(received), 1)
        self.assertEqual(received[0].payload, {"hp": 99})
        self.assertEqual(transport.sent, [])

    def test_server_receives_client_event_and_processes_locally(self):
        transport = FakeServerTransport()
        mediator = UMediator(transport)
        received = []
        mediator.register("input", received.append)

        mediator.ingest_remote_envelope(
            EventEnvelope(
                name="input",
                payload={"key": "space"},
                delivery=Delivery.TO_SERVER,
                origin="client_1",
                event_id="evt-client",
            )
        )
        mediator.update()

        self.assertEqual(len(received), 1)
        self.assertEqual(received[0].delivery, Delivery.TO_SERVER)
        self.assertEqual(received[0].origin, "client_1")
        self.assertEqual(transport.broadcasts, [])


if __name__ == "__main__":
    unittest.main()
