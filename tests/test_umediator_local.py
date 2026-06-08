import json
import os
import sys
import types
import unittest


SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from pyved_engine.umediator import Delivery, EventEnvelope, EventReadyCls, UMediator
from pyved_engine.umediator import netlayer_factory
from pyved_engine.umediator.netlayer_factory import build_netlayer_from_module


class FakeClientTransport:
    def __init__(self):
        self.registered = None
        self.sent = []
        self.broadcast_calls = 0

    def get_server_flag(self):
        return 0

    def start_comms(self, host_info, port_info):
        return None

    def send_to_server(self, envelope):
        self.sent.append(envelope)

    def broadcast_to_clients(self, envelope):
        self.broadcast_calls += 1
        raise AssertionError("client transport must not broadcast")

    def register_mediator(self, ref_mediator):
        self.registered = ref_mediator

    def shutdown_comms(self):
        return None


class FakeMediator:
    def __init__(self):
        self.calls = []

    def post(self, event_type, event=None, delivery=None):
        self.calls.append((event_type, event, delivery))


class ProtocolTests(unittest.TestCase):
    def test_envelope_roundtrip_from_dict_and_json(self):
        envelope = EventEnvelope(
            name="player_moved",
            payload={"x": 12, "y": 8},
            delivery=Delivery.TO_SERVER,
            origin="client_a",
            event_id="evt-1",
        )

        payload = envelope.to_json()
        rebuilt = EventEnvelope.from_json(payload)

        self.assertEqual(rebuilt.name, "player_moved")
        self.assertEqual(rebuilt.payload, {"x": 12, "y": 8})
        self.assertEqual(rebuilt.delivery, Delivery.TO_SERVER)
        self.assertEqual(rebuilt.origin, "client_a")
        self.assertEqual(rebuilt.event_id, "evt-1")

    def test_envelope_from_dict_accepts_json_loaded_payload(self):
        raw = {
            "name": "match_started",
            "payload": {"seed": 42},
            "delivery": "broadcast",
            "origin": "server",
            "event_id": "evt-2",
        }

        envelope = EventEnvelope.from_dict(raw)

        self.assertEqual(envelope.delivery, Delivery.BROADCAST)
        self.assertEqual(json.loads(envelope.to_json())["name"], "match_started")


class MediatorLocalTests(unittest.TestCase):
    def test_post_defaults_to_solo_mode_without_network_layer(self):
        mediator = UMediator()
        received = []
        mediator.register("solo_ping", received.append)

        mediator.post("solo_ping", {"value": 1})
        mediator.update()

        self.assertEqual(len(received), 1)
        self.assertEqual(received[0].delivery, Delivery.LOCAL)
        self.assertEqual(received[0].payload, {"value": 1})

    def test_client_local_event_dispatches_only_locally(self):
        transport = FakeClientTransport()
        mediator = UMediator(transport)
        received = []
        mediator.register("ping", received.append)

        mediator.post("ping", {"value": 1}, delivery=Delivery.LOCAL)
        mediator.update()

        self.assertEqual(len(received), 1)
        self.assertEqual(received[0].name, "ping")
        self.assertEqual(received[0].payload, {"value": 1})
        self.assertEqual(transport.sent, [])

    def test_client_cannot_broadcast(self):
        mediator = UMediator(FakeClientTransport())

        with self.assertRaises(RuntimeError):
            mediator.post("spawn", {"kind": "slime"}, delivery=Delivery.BROADCAST)

    def test_setting_network_layer_registers_mediator(self):
        transport = FakeClientTransport()
        mediator = UMediator()

        mediator.set_network_layer(transport)

        self.assertIs(transport.registered, mediator)
        self.assertFalse(mediator.is_server)


class FactoryAndHelperTests(unittest.TestCase):
    def test_event_ready_cls_uses_injected_mediator(self):
        fake = FakeMediator()

        class Demo(EventReadyCls):
            def __init__(self, mediator):
                super().__init__(mediator)

        demo = Demo(fake)
        demo.pev("hello", {"x": 1})

        self.assertEqual(len(fake.calls), 1)
        self.assertEqual(fake.calls[0][0], "hello")
        self.assertEqual(fake.calls[0][1], {"x": 1})
        self.assertEqual(fake.calls[0][2], Delivery.LOCAL)

    def test_netlayer_factory_exposes_new_transport_contract(self):
        fake_module = types.SimpleNamespace(
            get_server_flag=lambda: 0,
            start_comms=lambda host, port: ("start", host, port),
            send_to_server=lambda envelope: ("send", envelope),
            broadcast_to_clients=lambda envelope: ("broadcast", envelope),
            register_mediator=lambda mediator: ("register", mediator),
            shutdown_comms=lambda: ("shutdown",),
        )

        netlayer = build_netlayer_from_module(fake_module)

        self.assertTrue(hasattr(netlayer, "send_to_server"))
        self.assertTrue(hasattr(netlayer, "broadcast_to_clients"))
        self.assertTrue(hasattr(netlayer, "register_mediator"))

    def test_auto_transport_defaults_to_socket_on_native_runtime(self):
        old_brython = getattr(netlayer_factory, "__BRYTHON__", None)
        old_force = getattr(netlayer_factory, "FORCE_WS_TRANSPORT", None)
        try:
            if hasattr(netlayer_factory, "__BRYTHON__"):
                delattr(netlayer_factory, "__BRYTHON__")
            if hasattr(netlayer_factory, "FORCE_WS_TRANSPORT"):
                delattr(netlayer_factory, "FORCE_WS_TRANSPORT")

            self.assertEqual(netlayer_factory.resolve_transport_code("auto"), "SOCKET")

            netlayer = netlayer_factory.build_netlayer("auto", "client")
            self.assertIn("netw_socket_cli", netlayer.send_to_server.__module__)
        finally:
            if old_brython is not None:
                setattr(netlayer_factory, "__BRYTHON__", old_brython)
            elif hasattr(netlayer_factory, "__BRYTHON__"):
                delattr(netlayer_factory, "__BRYTHON__")
            if old_force is not None:
                setattr(netlayer_factory, "FORCE_WS_TRANSPORT", old_force)
            elif hasattr(netlayer_factory, "FORCE_WS_TRANSPORT"):
                delattr(netlayer_factory, "FORCE_WS_TRANSPORT")

    def test_brython_and_force_flags_choose_websocket_codes(self):
        old_brython = getattr(netlayer_factory, "__BRYTHON__", None)
        old_force = getattr(netlayer_factory, "FORCE_WS_TRANSPORT", None)
        try:
            setattr(netlayer_factory, "__BRYTHON__", True)
            if hasattr(netlayer_factory, "FORCE_WS_TRANSPORT"):
                delattr(netlayer_factory, "FORCE_WS_TRANSPORT")
            self.assertEqual(netlayer_factory.resolve_transport_code("auto"), "WEB_COMPAT_WS")

            setattr(netlayer_factory, "FORCE_WS_TRANSPORT", True)
            self.assertEqual(netlayer_factory.resolve_transport_code("auto"), "WEB_SOCKET_RELAY")

            netlayer = netlayer_factory.build_netlayer("auto", "server")
            self.assertIn("netw_ws_serv", netlayer.broadcast_to_clients.__module__)
        finally:
            if old_brython is not None:
                setattr(netlayer_factory, "__BRYTHON__", old_brython)
            elif hasattr(netlayer_factory, "__BRYTHON__"):
                delattr(netlayer_factory, "__BRYTHON__")
            if old_force is not None:
                setattr(netlayer_factory, "FORCE_WS_TRANSPORT", old_force)
            elif hasattr(netlayer_factory, "FORCE_WS_TRANSPORT"):
                delattr(netlayer_factory, "FORCE_WS_TRANSPORT")


if __name__ == "__main__":
    unittest.main()
