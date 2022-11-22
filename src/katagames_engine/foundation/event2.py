import re

from .defs import EngineEvTypes, KengiEv, PseudoEnum
from .defs import to_camelcase, to_snakecase, CircularBuffer, Singleton


_FIRST_LISTENER_ID = 72931


def game_events_enum(x_iterable):
    return PseudoEnum(x_iterable, EngineEvTypes.first + EngineEvTypes.size)


@Singleton
class EvManager:
    def __init__(self):
        self._etype_to_listenerli = dict()
        self._cbuffer = CircularBuffer()
        self._known_ev_types = dict()  # corresp nom event camelcase <-> identifiant num.
        self._etype_to_sncname = dict()  # corresp identifiant num. <-> nom event snakecase
        self.regexp = None
        self.debug_mode = False

        self.a_event_source = None

    @property
    def queue_size(self):
        return self._cbuffer.get_size()

    def post(self, etype, **kwargs):
        self._cbuffer.enqueue((etype, kwargs))

    def update(self):
        # optional block, in some cases this is equivalent to a <pass> instruction
        if self.a_event_source:  # true => pull all events from alt. source (concrete kengi backend) & merge in cbuffer
            for alien_ev in self.a_event_source.pull_events():
                kevent = (self.a_event_source.map_etype2kengi(alien_ev.type), alien_ev.dict)
                self._cbuffer.enqueue(kevent)

        while len(self._cbuffer.deque_obj):
            etype, d = self._cbuffer.dequeue()
            if etype in self._etype_to_listenerli:
                for lobj in self._etype_to_listenerli[etype]:
                    adhoc_meth_name = 'on_'+self._etype_to_sncname[etype]
                    getattr(lobj, adhoc_meth_name)(KengiEv(etype, **d))

    def hard_reset(self):
        self._etype_to_listenerli.clear()

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

    def setup(self, given_extra_penum=None):
        names = list()
        self._known_ev_types = EngineEvTypes.content.copy()

        for evname, eid in EngineEvTypes.content.items():
            names.append(to_snakecase(evname))

        if given_extra_penum is not None:
            self._known_ev_types.update(given_extra_penum.content)
            for evname, eid in given_extra_penum.content.items():
                names.append(to_snakecase(evname))

        # force a {refresh regexp} op!
        self._refresh_regexp(names)

        for ename_cc, etype in self._known_ev_types.items():
            self._etype_to_sncname[etype] = to_snakecase(ename_cc)


class Emitter:
    _free_listener_id = _FIRST_LISTENER_ID

    def __init__(self):
        self._manager = None
        cls = self.__class__
        self._lid = cls._free_listener_id
        cls._free_listener_id += 1

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
        if self._is_active:
            raise ValueError('call turn_on on obj {} where ._is_active is already True!'.format(self))

        if self._manager is None:
            self._manager = EvManager.instance()

        # introspection & detection des on_*
        # où * représente tout type d'évènement connu du moteur, que ce soit un event engine ou un event custom ajouté
        every_method = [method_name for method_name in dir(self) if callable(getattr(self, method_name))]
        callbacks_only = [mname for mname in every_method if self._manager.regexp.match(mname)]

        # BIG WARNING- important
        for e in every_method:
            if e[:3] == 'on_' and (e not in callbacks_only):
                rawmsg = '!!! BIG WARNING !!!\n    listener #{} that is{}\n'
                rawmsg += '    has been turned -ON- but its method "{}" cannot be called (Unknown event type)'
                w_msg = rawmsg.format(self.id, self, e)
                print(w_msg)

        for cbname in callbacks_only:
            # remove 'on_' prefix and convert Back to CamlCase
            self._tracked_ev.append(to_camelcase(cbname[3:]))

        # enregistrement de son activité d'écoute auprès du evt manager
        for evname in self._tracked_ev:
            self._manager.subscribe(evname, self)

        self._is_active = True

    def turn_off(self):
        # opération contraire
        for evname in self._tracked_ev:
            self._manager.unsubscribe(evname, self)
        del self._tracked_ev[:]
        self._is_active = False
