import katagames_engine as kengi


MyEvTypes = kengi.event.enum_ev_types(
    'Explosion',  # contains einfos: a 3-tuple of (i,j) pairs
    'SymSwap',  # contains two pairs: "ij_source" ; "ij_target"
    'ScoreUpdate'  # contains: "value"
)
