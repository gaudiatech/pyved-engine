import katagames_engine as kengi


# always try to keep your event number low: model->view or model->ctrl comms only
MyEvTypes = kengi.event.enum_ev_types(
    'ConvChoice',  # contains value
    'ConvEnds',
)
