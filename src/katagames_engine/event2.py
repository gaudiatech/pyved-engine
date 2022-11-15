import pygame

from .core import *


EngineEvTypes = PseudoEnum([
    'AppQuit',
    'KeyDown',
    'KeyUp',
    'MouseMotion',
    'MouseDown',
    'MouseUp',

    'Update',
    'Paint',

    'Gamestart',
    'Gameover',
    # (used in RPGs like niobepolis, conv<- conversation)
    'ConvStart',  # contains convo_obj, portrait
    'ConvFinish',
    'ConvStep',  # contains value

    'StateChange',  # contains code state_ident
    'StatePush',  # contains code state_ident
    'StatePop',

    'NetwSend',  # [num] un N°identification & [msg] un string (Async network comms)
    'NetwReceive'  # [num] un N°identification & [msg] un string (Async network comms)
], pygame.USEREVENT)

_pygame_to_kengi_etype = {
    256: EngineEvTypes.AppQuit,
    768: EngineEvTypes.KeyDown,
    769: EngineEvTypes.KeyUp,
    1024: EngineEvTypes.MouseMotion,
    1025: EngineEvTypes.MouseDown,
    1026: EngineEvTypes.MouseUp,
}


def game_events_enum(x_iterable):
    return PseudoEnum(x_iterable, EngineEvTypes.first + EngineEvTypes.size)


class KengiEv:
    def __init__(self, etype, **entries):
        self.__dict__.update(entries)
        self.type = etype


@Singleton
class EvManager:
    def __init__(self):
        self._etype_to_listenerli = dict()
        self._cbuffer = CircularBuffer()
        self._known_ev_types = dict()  # corresp nom event camelcase <-> identifiant num.
        self._etype_to_sncname = dict()  # corresp identifiant num. <-> nom event snakecase
        self.regexp = None
        self.debug_mode = False

    @property
    def queue_size(self):
        return self._cbuffer.get_size()

    def post(self, etype, **kwargs):
        self._cbuffer.enqueue((etype, kwargs))

    def update(self):
        # merge events stored in the backend with the kengi buffer
        try:
            for pygev in pygame.event.get():
                new_elt = (_pygame_to_kengi_etype[pygev.type], pygev.dict)
                self._cbuffer.deque_obj.append(new_elt)
                print('added --->>', new_elt[0], ' from pygame queue')
        except KeyError:
            pass  # no conversion
            # print(str(new_elt.dict))

        while len(self._cbuffer.deque_obj):
            # process event
            etype, d = self._cbuffer.dequeue()
            if etype in self._etype_to_listenerli:
                for lobj in self._etype_to_listenerli[etype]:
                    getattr(lobj, 'on_'+self._etype_to_sncname[etype])(KengiEv(etype, **d))

    def hard_reset(self):
        self._etype_to_listenerli.clear()
        self._cbuffer = CircularBuffer()
        self.event_types_inform()

    def _refresh_regexp(self, gnames):
        # we create a regexp such that, listeners know what keywords they have to consider
        # when analysing the list of their
        # .on_***
        # attribute methods
        regexp_prefix = '^on_(?:'
        rxp_body = '|'.join(gnames)
        regexp_sufix = '$)'
        # debug: print the updated regexp
        # -
        # print(regexp_prefix + rxp_body + regexp_sufix)
        self.regexp = re.compile(regexp_prefix + rxp_body + regexp_sufix)

    def subscribe(self, ename, listener_obj):
        cod = self._known_ev_types[ename]
        if cod not in self._etype_to_listenerli:
            self._etype_to_listenerli[cod] = list()

        self._etype_to_listenerli[cod].append(listener_obj)
        if self.debug_mode:
            print('  debug SUBSCRIBE - - - {} - {}'.format(ename, listener_obj))

    def unsubscribe(self, ename, listener_obj):
        cod = self._known_ev_types[ename]
        # if cod in self._etype_to_listenerli:
        try:
            self._etype_to_listenerli[cod].remove(listener_obj)
        except (KeyError, ValueError):
            print('***EvManager warning. Trying to remove listener_obj {}, not found!'.format(
                listener_obj.id
            ))
        if self.debug_mode:
            print('  debug UNSUBSCRIBE - - - {} - {}'.format(ename, listener_obj))

    def event_types_inform(self, given_extra_penum=None):
        names = list()
        self._known_ev_types = EngineEvTypes.content.copy()

        for evname, eid in EngineEvTypes.content.items():
            names.append(to_snakecase(evname))

        if given_extra_penum:
            self._known_ev_types.update(given_extra_penum.content)
            for evname, eid in given_extra_penum.content.items():
                names.append(to_snakecase(evname))

        # force a {refresh regexp} op!
        self._refresh_regexp(names)

        for ename_cc, etype in self._known_ev_types.items():
            self._etype_to_sncname[etype] = to_snakecase(ename_cc)


class Emitter:
    _free_listener_id = 34822

    def __init__(self):
        self._manager = None

        self._lid = self.__class__._free_listener_id
        self.__class__._free_listener_id += 1

    def pev(self, evtype, **kwargs):
        if self._manager is None:
            self._manager = EvManager.instance()
        self._manager.post(evtype, **kwargs)


class EvListener(Emitter):

    def __init__(self):
        super().__init__()
        self._is_active = False
        self._inspection_res = set()
        self._tracked_ev = list()

    @property
    def id(self):
        return self._lid

    def turn_on(self):
        if self._manager is None:
            self._ev_manager_ref = EvManager.instance()

        # introspection & detection des on_*
        # où * représente tout type d'évènement connu du moteur, que ce soit un event engine ou un event custom ajouté
        every_method = [method_name for method_name in dir(self) if callable(getattr(self, method_name))]
        callbacks_only = [mname for mname in every_method if self._ev_manager_ref.regexp.match(mname)]

        for cbname in callbacks_only:
            # remove 'on_' prefix and convert Back to CamlCase
            self._tracked_ev.append(to_camelcase(cbname[3:]))

        # enregistrement de son activité d'écoute auprès du evt manager
        for evname in self._tracked_ev:
            self._ev_manager_ref.subscribe(evname, self)

    def turn_off(self):
        # opération contraire
        for evname in self._tracked_ev:
            self._ev_manager_ref.unsubscribe(evname, self)
        del self._tracked_ev[:]
