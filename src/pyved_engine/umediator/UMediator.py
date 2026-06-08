import uuid

from .protocol import Delivery, EventEnvelope, ensure_envelope


class UMediator:
    def __init__(self, network_layer=None):
        self.ident = uuid.uuid4().hex[:12]
        self.listeners = {}
        self.event_queue = []
        self.network_layer = None
        self.is_server = False

        if network_layer is not None:
            self.set_network_layer(network_layer)

    def set_network_layer(self, ref):
        if self.network_layer is not None and self.network_layer is not ref:
            raise RuntimeError("a network layer is already attached to this mediator")
        self.network_layer = ref
        self.is_server = bool(ref.get_server_flag())
        ref.register_mediator(self)

    def register(self, event_type, listener):
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(listener)

    def unregister(self, event_type, listener):
        if event_type in self.listeners:
            try:
                self.listeners[event_type].remove(listener)
            except ValueError:
                pass
            if not self.listeners[event_type]:
                del self.listeners[event_type]

    def _basic_notify(self, event_type, event):
        if event_type in self.listeners:
            for listener_cb in list(self.listeners[event_type]):
                listener_cb(event)

    def post(self, event_type, event=None, delivery=Delivery.LOCAL, origin=None, event_id=None):
        envelope = EventEnvelope(
            name=event_type,
            payload={} if event is None else event,
            delivery=delivery,
            origin=self.ident if origin is None else origin,
            event_id=event_id,
        )
        if self.network_layer is None:
            envelope.delivery = Delivery.LOCAL
        elif envelope.delivery == Delivery.BROADCAST and not self.is_server:
            raise RuntimeError("only the server mediator can broadcast events")
        self.event_queue.append(envelope)
        return envelope.event_id

    def ingest_remote_envelope(self, envelope):
        normalized = ensure_envelope(envelope)
        if self.network_layer is None or (not self.is_server and normalized.delivery == Delivery.BROADCAST):
            normalized.delivery = Delivery.LOCAL
        self.event_queue.append(normalized)

    def _notify_local(self, envelope):
        self._basic_notify(envelope.name, envelope)

    def update(self):
        pending_count = len(self.event_queue)
        while pending_count > 0:
            envelope = self.event_queue.pop(0)
            pending_count -= 1

            if envelope.delivery == Delivery.LOCAL:
                self._notify_local(envelope)
                continue

            if envelope.delivery == Delivery.TO_SERVER:
                if self.is_server:
                    self._notify_local(envelope)
                else:
                    if self.network_layer is None:
                        self._notify_local(envelope)
                        continue
                    self.network_layer.send_to_server(envelope)
                continue

            if envelope.delivery == Delivery.BROADCAST:
                if self.network_layer is None:
                    self._notify_local(envelope)
                    continue
                if not self.is_server:
                    raise RuntimeError("client mediators cannot broadcast events")
                self._notify_local(envelope)
                if self.network_layer is None:
                    raise RuntimeError("no network layer is attached to this server mediator")
                self.network_layer.broadcast_to_clients(envelope)
                continue

            raise ValueError(f"unsupported delivery mode: {envelope.delivery}")

    def __repr__(self):
        role = "server" if self.is_server else "client"
        return f"<UMediator {role} {self.ident}>"
