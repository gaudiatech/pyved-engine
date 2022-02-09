from ..StContainer import StContainer
from .defs import EngineEvTypes
from .gfx_updater import display_update
from .events import EventReceiver
from .structures import Stack


class GameTicker(EventReceiver):
    def __init__(self, pygame_pym, xmaxfps):
        self.pygame_pym = pygame_pym

        super().__init__(1)  # id de gameobject 1
        self._running = True
        self._clock = self.pygame_pym.time.Clock()
        self._maxfps = xmaxfps

    @property
    def running(self):
        return self._running

    def proc_event(self, ev, source):
        if ev.type == self.pygame_pym.QUIT or ev.type == EngineEvTypes.GAMEENDS:
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
            display_update()

            self._clock.tick(self._maxfps)


# -  --  - - --
#  basé sur (GameTicker.
# - - -  - -
class StackBasedGameCtrl(EventReceiver):

    def __init__(self, existing_ticker, gamestates_enum, stmapping, glvars_pymodule, katagame_st=None, ):
        super().__init__(sticky=True)

        self.ticker = existing_ticker
        self.pygame_pym = existing_ticker.pygame_pym

        # lets build up all gamestates objects
        self._st_container = StContainer.instance()
        self._st_container.setup(gamestates_enum, stmapping, glvars_pymodule)

        if katagame_st:
            self.first_state_id = -1
            self._st_container.hack_bios_state(katagame_st)
        else:
            self.first_state_id = 0

        self.__state_stack = Stack()

    # redefinition
    def halt(self):
        while self.get_curr_state_ident() is not None:
            self._pop_state()
        self.ticker.halt()

    def get_curr_state_ident(self):
        return self.__state_stack.peek()

    def proc_event(self, ev, source):
        if ev.type == self.pygame_pym.QUIT or ev.type == EngineEvTypes.GAMEENDS:
            self.halt()

        elif ev.type == EngineEvTypes.PUSHSTATE:
            state_obj = self._st_container.retrieve(ev.state_ident)
            self._push_state(state_obj)

        elif ev.type == EngineEvTypes.POPSTATE:
            self._pop_state()

        elif ev.type == EngineEvTypes.CHANGESTATE:
            state_obj = self._st_container.retrieve(ev.state_ident)
            self._change_state(state_obj)

    def loop(self):
        self.__state_stack.push(self.first_state_id)
        self._st_container.retrieve(self.first_state_id).enter()

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
