"""
Rule:
- a game cartridge relies solely on the engine. The _ref_engine
that a game launcher uses will be cloned and become readable from here

- elements that you find in .looparts rely either on the engine itself,
 or on the sublayer for their implementation
The current file gets imported by any "shard"/ element of .looparts
"""


_ref_sublayer = None
_engine = None
_hub = {}  # in order to register pyv submodules as they're lazy-loaded. This idea is useful because submodules may
# also create dependencies between them, but we do not want the engine dev to think about the loading/import order
# whenever he/she is writing a new pyv submodule


def set_sublayer(x):
    global _ref_sublayer
    if _ref_sublayer:
        raise RuntimeError('should no set _ref_sublayer more than once!')
    _ref_sublayer = x


def get_sublayer():
    return _ref_sublayer


def save_engine_ref(x):
    global _engine
    _engine = x  # storing a reference to the ngine itself. Useful when writing pyv submodules!


def ref_engine():
    if _engine is None:
        raise RuntimeError('asking for ref engine while the ref hasnt been saved yet!')
    return _engine
