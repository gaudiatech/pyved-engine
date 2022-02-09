import json
import time
import weakref
from abc import abstractmethod
from . import conf_eng as engineconf
from .defs import EngineEvTypes, FIRST_CUSTO_TYPE, USEREVENT
from collections import deque as deque_obj

PygameBridge = None


# flag/basic queue for headless mode
headless_mode = False
simu_queue = list()
gl_unique_manager = None


class EventManager:
    @classmethod
    def instance(cls):
        global gl_unique_manager
        return gl_unique_manager


class CgmEvent:
    ETYPE_ATTR_NAME = 'cgm_type'
    ref_enum_custom = None

    def __init__(self, engin_ev_type, **kwargs):
        if engin_ev_type == USEREVENT:
            raise ValueError('ev_type {} is not valid (cgm reserved type)')

        self.type = engin_ev_type
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def inject_custom_names(cls, ref_enum):
        cls.ref_enum_custom = ref_enum

    @staticmethod
    def ext_tev_detection(etype):
        # extended type event detection
        return etype == USEREVENT

    @classmethod
    def deserialize(cls, ser):
        # print(ser)
        tmpli = ser.split('@')
        adhoc_type = int(tmpli[0])
        dico = json.loads(tmpli[1])
        if adhoc_type == EngineEvTypes.PAINT:
            dico['screen'] = engineconf.screen
        return cls(adhoc_type, **dico)

    def serialize(self):
        kwargs_cp = dict()
        for k, v in self.__dict__.items():
            if k == 'type':
                pass
            elif k == 'screen' and self.type == EngineEvTypes.PAINT:
                kwargs_cp['screen'] = None
            elif isinstance(v, tuple):
                kwargs_cp[k] = list(v)
            else:
                kwargs_cp[k] = v

        return '{}@'.format(self.type) + json.dumps(kwargs_cp)

    def wrap(self):
        """
        :return: a corresponding pygame event object, so it can be put on the pygame queue
        """
        tmp = self.__dict__.copy()
        if self.type > USEREVENT:
            tmp[self.ETYPE_ATTR_NAME] = self.type
            t = USEREVENT
        else:
            t = self.type
        del tmp['type']
        return kpygame.PygameEvent(t, tmp)

    @classmethod
    def unwrap(cls, pygam_ev_obj):
        assert pygam_ev_obj.type == USEREVENT
        engin_type = getattr(pygam_ev_obj, cls.ETYPE_ATTR_NAME)

        tmp = pygam_ev_obj.dict
        del tmp[cls.ETYPE_ATTR_NAME]
        return cls(engin_type, **tmp)  # instanciation CgmEvent

    def __str__(self):
        if self.type > USEREVENT:
            if self.type < FIRST_CUSTO_TYPE:
                nom = EngineEvTypes.inv_map[self.type]
            elif self.ref_enum_custom is None:
                nom = '????'
            else:
                nom = self.ref_enum_custom.inv_map[self.type]
        else:
            nom = kpygame.event.event_name(self.type)
        tmp = self.__dict__.copy()
        del tmp['type']
        return '<CgmEvent({}-{} {})>'.format(self.type, nom, tmp)


class CogObject:
    """
    basic cogmonger object,
    grants access to utility methods:
    - get_id()
    - pev(ev_type, ...)
    """

    _instances_clue = set()
    _unavailable_ids = set()
    _next_id = 0

    # cached events
    lu_cached_ev = None
    paint_cached_ev = None

    # contains time from webctx
    wt = None

    # we can send 'N times' the logic update event
    # while keeping the same time.time() value
    # => this speeds up the game without loosing too much precision on time handling
    _optim_counter = 0
    _n_times_same_timeval = 100

    def __init__(self, explicit_id=None):
        global gl_unique_manager

        # - module events, init procedure...
        if CogObject.lu_cached_ev is None:
            CogObject.lu_cached_ev = CgmEvent(EngineEvTypes.LOGICUPDATE, curr_t=None)
            CogObject.paint_cached_ev = CgmEvent(EngineEvTypes.PAINT, screen=None)

        # resuming constructor
        self._manager = gl_unique_manager

        # - attribue un nouvel _id pour cette instance de CogObject
        self._id = self.__trouve_nouvel_id() if (explicit_id is None) else explicit_id
        self.__class__._unavailable_ids.add(self._id)

        # - garde trace de cette nouvelle instance...
        self._instances_clue.add(weakref.ref(self))

    @classmethod
    def __trouve_nouvel_id(cls):
        while cls._next_id in cls._unavailable_ids:
            cls._next_id += 1
        res = cls._next_id
        return res

    def get_id(self):
        return self._id

    @classmethod
    def __list_instances(cls):
        dead = set()
        for ref in cls._instances_clue:
            obj = ref()
            if obj is not None:
                yield obj
            else:
                dead.add(ref)
        cls._instances_clue -= dead

    @classmethod
    def select_by_id(cls, given_id):
        for obj in cls.__list_instances():
            if given_id == obj.get_id():
                return obj
        print('**warning requested CogObject [id={}] not found'.format(given_id))

    def pev(self, ev_type, **kwargs):
        if ev_type == EngineEvTypes.LOGICUPDATE:
            if CogObject.wt:
                CogObject.lu_cached_ev.curr_t = CogObject.wt
            else:
                CogObject.lu_cached_ev.curr_t = time.time()
            self._manager.post(CogObject.lu_cached_ev)

        elif ev_type == EngineEvTypes.PAINT:
            CogObject.paint_cached_ev.screen = engineconf.screen
            self._manager.post(CogObject.paint_cached_ev)

        else:
            ev = CgmEvent(ev_type, **kwargs)
            self._manager.post(ev)


class EventReceiver(CogObject):

    def __init__(self, sticky=False):
        super().__init__()
        self._sticky = sticky  # if True, the receiver won't get removed when the EventManager soft resets
        self._active_receiver = False

    @property
    def sticky(self):
        return self._sticky

    def is_active(self):
        return self._active_receiver

    def turn_on(self):
        self._manager.add_listener(self)
        self._active_receiver = True

    def turn_off(self):
        self._manager.remove_listener(self)
        self._active_receiver = False

    @abstractmethod
    def proc_event(self, ev, source):
        raise NotImplementedError


# class EventDispatcher:
#
#     def __init__(self):
#         self._queue = list()
#
#     def add_listener(self, obj: EventReceiver):
#         self._queue.append(obj)
#
#     def prioritize(self, obj):
#         self._queue.remove(obj)
#         self._queue.insert(0, obj)
#
#     def postpone(self, obj):
#         self._queue.remove(obj)
#         self._queue.append(obj)
#
#     def remove_listener(self, obj):
#         self._queue.remove(obj)
#
#     def soft_reset(self):
#         nl = list()
#         for memb in self._queue:
#             if memb.is_sticky():
#                 nl.append(memb)
#         self._queue = nl
#
#     def hard_reset(self):
#         del self._queue[:]
#
#     def count_listeners(self):
#         return len(self._queue)
#
#     def dispatch(self, cgm_event, dispatcher):
#         """
#         :param cgm_event: instance of CgmEvent class, includes a type
#         :param dispatcher: None denotes the general EventDispatcher
#         """
#         for recv in self._queue:
#             if recv.proc_event(cgm_event, dispatcher):
#                 return


# @Singleton
# class EventManager(EventDispatcher):
#     """
#     the root source for all events
#     """
#
#     def post(self, given_evt):
#         global headless_mode, simu_queue
#         if headless_mode:
#             simu_queue.append(given_evt.wrap())
#         else:
#             pygame.event.post(given_evt.wrap())
#
#     def update(self):
#         global headless_mode, simu_queue
#
#         if headless_mode:  # HEADLESS mode
#             simu_queue.reverse()
#             while len(simu_queue) > 0:
#                 rev = simu_queue.pop()
#                 if not CgmEvent.ext_tev_detection(rev.type):  # ev. classique
#                     self.dispatch(rev, None)
#                 else:
#                     cgm_ev = CgmEvent.unwrap(rev)  # ev. étendu
#                     self.dispatch(cgm_ev, None)
#             return
#
#         rev = pygame.event.poll()
#         while rev.type != pygame.NOEVENT:
#             if not CgmEvent.ext_tev_detection(rev.type):  # ev. classique
#                 self.dispatch(rev, None)
#             else:
#                 cgm_ev = CgmEvent.unwrap(rev)  # ev. étendu
#                 self.dispatch(cgm_ev, None)
#
#             rev = pygame.event.poll()


class ListenerSet:
    def __init__(self):
        self._corresp = dict()
        self._listener_ids = list()

    def add_listener(self, cog_obj):
        key = cog_obj.get_id()
        self._corresp[key] = cog_obj
        self._listener_ids.append(key)

    def remove_listener(self, cog_obj):
        key = cog_obj.get_id()
        self._listener_ids.remove(key)
        del self._corresp[key]

    def hard_reset(self):
        del self._listener_ids[:]
        self._corresp.clear()

    def soft_reset(self):
        ids_tbr = set()
        for l_id in self._listener_ids:
            if not self._corresp[l_id].sticky:
                ids_tbr.add(l_id)
        for adhoc_id in ids_tbr:
            self._listener_ids.remove(adhoc_id)
            del self._corresp[adhoc_id]

    def __getitem__(self, k):
        return self._corresp[k]

    def __iter__(self):
        return self._listener_ids.__iter__()


class DeadSimpleManager:
    nb_inst = 0

    def __init__(self, pygame_pym):
        self.__class__.nb_inst += 1
        if self.__class__.nb_inst > 1:
            raise ValueError('using 2+ instances of DeadSimpleManager is forbidden')

        self._ref_ls = ListenerSet()
        self.add_listener = self._ref_ls.add_listener
        self.remove_listener = self._ref_ls.remove_listener
        self.hard_reset = self._ref_ls.hard_reset
        self.soft_reset = self._ref_ls.soft_reset

        self.pygame_pym = pygame_pym
        self._omega_mouse_events = {
            pygame_pym.MOUSEMOTION,
            pygame_pym.MOUSEBUTTONDOWN,
            pygame_pym.MOUSEBUTTONUP
        }
        self._ev_queue = deque_obj()

    def get_pressed_keys(self):
        return self.pygame_pym.key.get_pressed()

    def post(self, ev):
        self._ev_queue.appendleft(ev)

    def update(self):
        for alien_ev in self.pygame_pym.event.get():
            # if alien_ev.type in self._omega_mouse_events:
            #    alien_ev.pos = engineconf.conv_to_vscreen(*alien_ev.pos)
            self._ev_queue.appendleft(alien_ev)

        n = len(self._ev_queue)
        for _ in range(n):
            curr_ev = self._ev_queue.pop()
            for cogobj_id in self._ref_ls:
                blocking = self._ref_ls[cogobj_id].proc_event(curr_ev, None)
                if blocking:
                    continue
