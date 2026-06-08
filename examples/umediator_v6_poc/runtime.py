from __future__ import annotations

from pyved_engine.umediator import netlayer_factory


def configure_transport_flags(force_ws: bool):
    if force_ws:
        netlayer_factory.FORCE_WS_TRANSPORT = True
    elif hasattr(netlayer_factory, "FORCE_WS_TRANSPORT"):
        delattr(netlayer_factory, "FORCE_WS_TRANSPORT")

