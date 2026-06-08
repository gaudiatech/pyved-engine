import json
import uuid
from dataclasses import dataclass, field
from enum import Enum


class Delivery(Enum):
    LOCAL = "local"
    TO_SERVER = "to_server"
    BROADCAST = "broadcast"


@dataclass
class EventEnvelope:
    name: str
    payload: dict = field(default_factory=dict)
    delivery: Delivery = Delivery.LOCAL
    origin: str | None = None
    event_id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("event name must be a non-empty string")
        if self.payload is None:
            self.payload = {}
        if not isinstance(self.payload, dict):
            raise TypeError("event payload must be a dict or None")
        if not isinstance(self.delivery, Delivery):
            self.delivery = Delivery(self.delivery)

    def to_dict(self):
        return {
            "name": self.name,
            "payload": self.payload,
            "delivery": self.delivery.value,
            "origin": self.origin,
            "event_id": self.event_id,
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise TypeError("event envelope data must be a dict")
        payload = data.get("payload")
        if payload is None:
            payload = {}
        return cls(
            name=data["name"],
            payload=payload,
            delivery=Delivery(data.get("delivery", Delivery.LOCAL.value)),
            origin=data.get("origin"),
            event_id=data.get("event_id") or uuid.uuid4().hex,
        )

    @classmethod
    def from_json(cls, raw_text):
        return cls.from_dict(json.loads(raw_text))


def ensure_envelope(value):
    if isinstance(value, EventEnvelope):
        return value
    if isinstance(value, dict):
        return EventEnvelope.from_dict(value)
    if isinstance(value, str):
        return EventEnvelope.from_json(value)
    raise TypeError(f"unsupported envelope type: {type(value).__name__}")
