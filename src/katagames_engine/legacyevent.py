import time
from abc import abstractmethod
from collections import deque as deque_obj

from .compo import vscreen
from . import _hub
from . import struct
from .foundation import defs


enum_builder_generic = struct.enum_builder_generic
gl_unique_manager = None


def create_manager():
    global gl_unique_manager
    if gl_unique_manager is None:
        gl_unique_manager = DeadSimpleManager()
    else:
        print('* warning: second call to event.create_manager()')


def _enum_engine_ev_types(*sequential, **named):
    return enum_builder_generic(True, defs.FIRST_ENGIN_TYPE, *sequential, **named)


# disable on purpose this legacy system!
_EngineEvTypes = _enum_engine_ev_types(
    'LogicUpdate',
    'Paint',
    'RefreshScreen',

    'PushState',  # contient un code state_ident
    'PopState',
    'ChangeState',  # contient un code state_ident

    'GameBegins',  # correspond à l'ancien InitializeEvent
    'GameEnds',  # indique que la sortie de jeu est certaine

    'BtClick',

    'ConvChoice',  # contains value (used in rpgs like niobepolis, conv means conversation)
    'ConvStarts',  # contains convo_obj, portrait
    'ConvEnds',

    'FocusCh',
    'FieldCh',
    'DoAuth',

    'AsyncRecv',  # [num] un N°identification & [msg] un string
    'AsyncSend'  # [num] un N°identification & [msg] un string
)


def enum_ev_types(*sequential, **named):  # Custom events /!\ not engine events
    # this function should be used by the custom game
    return enum_builder_generic(False, defs.FIRST_CUSTO_TYPE, *sequential, **named)


class EventManager:
    @classmethod
    def instance(cls):
        global gl_unique_manager
        return gl_unique_manager


class CgmEvent:
    ETYPE_ATTR_NAME = 'cgm_type'
    ref_enum_custom = None

    def __init__(self, engin_ev_type, **kwargs):
        if engin_ev_type == defs.USEREVENT:
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
        return etype == defs.USEREVENT

    # @classmethod
    # def deserialize(cls, ser):
    #     # print(ser)
    #     tmpli = ser.split('@')
    #     adhoc_type = int(tmpli[0])
    #     dico = json.loads(tmpli[1])
    #     if adhoc_type == EngineEvTypes.PAINT:
    #         dico['screen'] = shared.screen
    #     return cls(adhoc_type, **dico)
    #
    # def serialize(self):
    #     kwargs_cp = dict()
    #     for k, v in self.__dict__.items():
    #         if k == 'type':
    #             pass
    #         elif k == 'screen' and self.type == EngineEvTypes.PAINT:
    #             kwargs_cp['screen'] = None
    #         elif isinstance(v, tuple):
    #             kwargs_cp[k] = list(v)
    #         else:
    #             kwargs_cp[k] = v
    #     return '{}@'.format(self.type) + json.dumps(kwargs_cp)

    # ---------- était utile jadis pour faire passer les event sur la file pygame classique --------
    # TODO decider du sort, now 2022

    # def wrap(self):
    #     """
    #     :return: a corresponding pygame event object, so it can be put on the pygame queue
    #     """
    #     tmp = self.__dict__.copy()
    #     if self.type > USEREVENT:
    #         tmp[self.ETYPE_ATTR_NAME] = self.type
    #         t = USEREVENT
    #     else:
    #         t = self.type
    #     del tmp['type']
    #     return kpygame.PygameEvent(t, tmp)
    #
    # @classmethod
    # def unwrap(cls, pygam_ev_obj):
    #     assert pygam_ev_obj.type == USEREVENT
    #     engin_type = getattr(pygam_ev_obj, cls.ETYPE_ATTR_NAME)
    #
    #     tmp = pygam_ev_obj.dict
    #     del tmp[cls.ETYPE_ATTR_NAME]
    #     return cls(engin_type, **tmp)

    # def __str__(self):
    #     if self.type > defs.USEREVENT:
    #         if self.type < defs.FIRST_CUSTO_TYPE:
    #             nom = EngineEvTypes.inv_map[self.type]
    #         elif self.ref_enum_custom is None:
    #             nom = '????'
    #         else:
    #             nom = self.ref_enum_custom.inv_map[self.type]
    #     else:
    #         nom = 'event classique pygame, code:' + str(self.type)
    #     tmp = self.__dict__.copy()
    #     del tmp['type']
    #     return '<CgmEvent({}-{} {})>'.format(self.type, nom, tmp)


# class CogObject:
#     _instances_clue = set()
#     _unavailable_ids = set()
#     _next_id = 0
#
#     # cached events
#     lu_cached_ev = None
#     paint_cached_ev = None
#
#     # contains time from webctx
#     wt = None
#
#     # we can send 'N times' the logic update event
#     # while keeping the same time.time() value
#     # => this speeds up the game without loosing too much precision on time handling
#     _optim_counter = 0
#     _n_times_same_timeval = 100
#
#     def __init__(self, explicit_id=None):
#         global gl_unique_manager
#
#         # - module events, init procedure...
#         if CogObject.lu_cached_ev is None:
#             CogObject.lu_cached_ev = CgmEvent(EngineEvTypes.LOGICUPDATE, curr_t=None)
#             CogObject.paint_cached_ev = CgmEvent(EngineEvTypes.PAINT, screen=None)
#
#         # resuming constructor
#         self._manager = gl_unique_manager
#
#         # - attribue un nouvel _id pour cette instance de CogObject
#         self._id = self.__trouve_nouvel_id() if (explicit_id is None) else explicit_id
#         self.__class__._unavailable_ids.add(self._id)
#
#         # - garde trace de cette nouvelle instance...
#         self._instances_clue.add(weakref.ref(self))
#
#     @classmethod
#     def __trouve_nouvel_id(cls):
#         while cls._next_id in cls._unavailable_ids:
#             cls._next_id += 1
#         res = cls._next_id
#         return res
#
#     def get_id(self):
#         return self._id
#
#     @classmethod
#     def __list_instances(cls):
#         dead = set()
#         for ref in cls._instances_clue:
#             obj = ref()
#             if obj is not None:
#                 yield obj
#             else:
#                 dead.add(ref)
#         cls._instances_clue -= dead
#
#     @classmethod
#     def select_by_id(cls, given_id):
#         for obj in cls.__list_instances():
#             if given_id == obj.get_id():
#                 return obj
#         print('**warning requested CogObject [id={}] not found'.format(given_id))
#
#     def pev(self, ev_type, **kwargs):
#         if ev_type == EngineEvTypes.LOGICUPDATE:
#
#             if CogObject.wt:
#                 CogObject.lu_cached_ev.curr_t = CogObject.wt
#             else:
#                 CogObject.lu_cached_ev.curr_t = time.time()
#             rdy_ev = CogObject.lu_cached_ev
#
#         elif ev_type == EngineEvTypes.PAINT:
#
#             CogObject.paint_cached_ev.screen = shared.screen
#             rdy_ev = CogObject.paint_cached_ev
#
#         else:
#
#             rdy_ev = CgmEvent(ev_type, **kwargs)
#
#         self._manager.post(rdy_ev)


class CogObj:
    _free_id = 2
    _taken = set()

    @classmethod
    def reset_class_state(cls):
        cls._free_id = 2
        cls._taken.clear()

    def __init__(self, specifyid=None):
        if specifyid:
            myid = specifyid
        else:
            cls = self.__class__
            while cls._free_id in cls._taken:
                cls._free_id += 1
            myid = cls._free_id
        self.__class__._taken.add(myid)
        self._ident = myid
        self._ev_cache = dict()
        self.manager = EventManager.instance()

    def get_id(self):
        return self._ident

    def pev(self, ev_type, **kwargs):
        try:
            eev = self._ev_cache[ev_type]
            eev.__dict__.update(kwargs)
            self.manager.post(eev)
        except KeyError:
            new_ev = CgmEvent(ev_type, **kwargs)
            if ev_type == EngineEvTypes.PAINT:
                new_ev.screen = vscreen.screen

            self._ev_cache[ev_type] = new_ev
            self.manager.post(new_ev)


class EventReceiver(CogObj):

    def __init__(self, explicit_id=None, sticky=False):
        """
        if sticky==True, the receiver won't be removed when "EventManager.soft_reset()"s
        """
        super().__init__(explicit_id)
        self._manager = gl_unique_manager
        self.sticky = sticky

    @property
    def active(self):
        return self._manager.talks_to(self)

    def turn_on(self):
        self._manager.add_listener(self)
        return self

    def turn_off(self):
        self._manager.remove_listener(self)

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

    def test_contains_id(self, k):
        return k in self._listener_ids

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

    def __init__(self):
        self.__class__.nb_inst += 1
        if self.__class__.nb_inst > 1:
            raise ValueError('using 2+ instances of DeadSimpleManager is forbidden')

        self._ref_ls = ListenerSet()
        self.add_listener = self._ref_ls.add_listener
        self.remove_listener = self._ref_ls.remove_listener
        self.hard_reset = self._ref_ls.hard_reset
        self.soft_reset = self._ref_ls.soft_reset

        self.pyg = _hub.pygame

        self._omega_mouse_events = {
            self.pyg.MOUSEMOTION,
            self.pyg.MOUSEBUTTONDOWN,
            self.pyg.MOUSEBUTTONUP
        }
        self._ev_queue = deque_obj()

    def talks_to(self, cogobj):
        return self._ref_ls.test_contains_id(cogobj.get_id())

    def get_pressed_keys(self):
        return _hub.pygame.key.get_pressed()

    def post(self, ev):
        self._ev_queue.appendleft(ev)

    def update(self):
        for alien_ev in _hub.pygame.event.get():
            self._ev_queue.appendleft(alien_ev)

        n = len(self._ev_queue)
        for _ in range(n):
            curr_ev = self._ev_queue.pop()
            for cogobj_id in self._ref_ls:
                blocking = self._ref_ls[cogobj_id].proc_event(curr_ev, None)
                if blocking:
                    continue


# ------ avant ct runners.py
class GameTicker(EventReceiver):
    def __init__(self, xmaxfps=None):
        super().__init__(explicit_id=1)

        self._running = True
        self.pyg = _hub.pygame
        self._clock = self.pyg.time.Clock()
        self.maxfps = xmaxfps

    @property
    def running(self):
        return self._running

    def proc_event(self, ev, source):
        if ev.type == self.pyg.QUIT or ev.type == EngineEvTypes.GAMEENDS:
            self.halt()

    def halt(self):
        self._running = False

    @property
    def clock(self):
        return self._clock

    def loop(self):
        while self._running:  # many iterations with only this line
            self.pev(EngineEvTypes.LOGICUPDATE)
            self.pev(EngineEvTypes.PAINT)

            self._manager.update()
            vscreen.flip()
            self._clock.tick(self.maxfps)


# -  --  - - --
#  basé sur (GameTicker.
# - - -  - -
class StackBasedGameCtrl(EventReceiver):

    def __init__(self, existing_ticker, gamestates_enum, glvars_pymodule, stmapping):
        super().__init__(sticky=True)

        self.ticker = existing_ticker
        # lets build up all gamestates objects
        self._st_container = struct.StContainer()

        # relation avec stcontainer
        self._st_container.setup(gamestates_enum, stmapping, glvars_pymodule)

        if -1 in stmapping:  # TODO fix architecture, engine shouldnt know bout SDK feat
            self.first_state_id = -1
        else:
            self.first_state_id = 0

        self.__state_stack = struct.Stack()

    # redefinition
    def halt(self):
        while self.get_curr_state_ident() is not None:
            self._pop_state()
        self.ticker.halt()

    def get_curr_state_ident(self):
        return self.__state_stack.peek()

    def proc_event(self, ev, source):
        if ev.type == _hub.pygame.QUIT or ev.type == EngineEvTypes.GAMEENDS:
            self.halt()

        elif ev.type == EngineEvTypes.PUSHSTATE:
            state_obj = self._st_container.retrieve(ev.state_ident)
            self._push_state(state_obj)

        elif ev.type == EngineEvTypes.POPSTATE:
            self._pop_state()

        elif ev.type == EngineEvTypes.CHANGESTATE:
            state_obj = self._st_container.retrieve(ev.state_ident)
            self._change_state(state_obj)

    def init_state0(self):
        self.__state_stack.push(self.first_state_id)
        self._st_container.retrieve(self.first_state_id).enter()

    def loop(self):
        self.init_state0()
        print('stack based ctrl loop STARTS!')
        self.ticker.loop()

    # --- ---
    #  MÉTIER
    # --- ---
    def _push_state(self, state_obj):
        tmp = self.__state_stack.peek()
        curr_state = self._st_container.retrieve(tmp)
        curr_state.pause()

        self.__state_stack.push(state_obj.get_id())
        state_obj.enter()

    def _pop_state(self):
        self.__only_the_pop_part()

        # FOLLOW - UP
        if self.__state_stack.count() == 0:
            self.ticker.halt()
            print('state count 0')
        else:
            tmp = self.__state_stack.peek()
            state_obj = self._st_container.retrieve(tmp)
            state_obj.resume()

    def _change_state(self, state_obj):
        self.__only_the_pop_part()

        # FOLLOW - UP
        self.__state_stack.push(state_obj.get_id())
        state_obj.enter()

    # Warning! never, ever call this method without some kind of follow-up (private method)
    def __only_the_pop_part(self):
        tmp = self.__state_stack.pop()
        state_obj = self._st_container.retrieve(tmp)
        state_obj.release()
