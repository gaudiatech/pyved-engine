USEREVENT = 27


# -- constants
FIRST_ENGIN_TYPE = USEREVENT + 1
FIRST_CUSTO_TYPE = FIRST_ENGIN_TYPE + 20  # therefore, 20 is the maximal amount of engine events


vernum = '0.0.4'  # before december 13th, 2020


from katagames_sdk.capsule.struct.misc import enum_builder_generic


def enumeration_pr_events_engine(*sequential, **named):
    return enum_builder_generic(True, FIRST_ENGIN_TYPE, *sequential, **named)


def enum_for_custom_event_types(*sequential, **named):
    return enum_builder_generic(False, FIRST_CUSTO_TYPE, *sequential, **named)


EngineEvTypes = enumeration_pr_events_engine(
    'LogicUpdate',
    'Paint',
    'RefreshScreen',

    'PushState',  # contient un code state_ident
    'PopState',
    'ChangeState',  # contient un code state_ident

    'GameBegins',  # correspond à l'ancien InitializeEvent
    'GameEnds',  # indique que la sortie de jeu est certaine

    'FocusCh',
    'FieldCh',
    'DoAuth',

    'AsyncRecv',  # [num] un N°identification & [msg] un string
    'AsyncSend'  # [num] un N°identification & [msg] un string
)
