import time

from . import vars
from .compo import vscreen
from ._hub import events
from .core.events import EngineEvTypes  # latest version of event sys
from .custom_struct import Stack, StContainer


multistate_flag = False
stack_based_ctrl = None
state_stack = None


class StateStackCtrl(events.EvListener):
    def __init__(self, all_gs, stmapping):
        super().__init__()
        self._gs_omega = all_gs
        self._stack = Stack()
        # CONVENTION: the first of the enum <=> the init gamestate id !
        self.first_state_id = all_gs.all_codes[0]
        self._st_container = StContainer()
        self._st_container.setup(all_gs, stmapping, None)
        self.__state_stack = Stack()

        self.gameover = False

    def get_state_by_code(self, k):
        return self._st_container.retrieve(k)

    def state_code_to_str(self, x):
        return self._gs_omega.inv_map[x]

    def turn_on(self):
        super().turn_on()
        print('>>>>>>>>>* Note: State stack is OPERATIONAL *')

    @property
    def current(self):
        return self.__state_stack.peek()

    # (it's a private method)
    # WARNING: never, ever call that method without a kind of follow-up
    def __only_the_pop_part(self):
        tmp = self.__state_stack.pop()
        state_obj = self._st_container.retrieve(tmp)
        state_obj.release()

    def _change_state(self, state_obj):
        self.__only_the_pop_part()
        self.__state_stack.push(state_obj.get_id())
        state_obj.enter()

    def _push_state(self, state_obj):
        tmp = self.__state_stack.peek()
        curr_state = self._st_container.retrieve(tmp)
        curr_state.pause()
        self.__state_stack.push(state_obj.get_id())
        state_obj.enter()

    def _pop_state(self):
        self.__only_the_pop_part()
        print('remains:', self.__state_stack.count())
        if self.__state_stack.count() > 0:
            tmp = self.__state_stack.peek()
            state_obj = self._st_container.retrieve(tmp)
            state_obj.resume()
        else:
            vars.gameover = True

    # --------------------
    #  CALLBACKS
    # --------------------
    def on_gamestart(self, ev):
        self.__state_stack.push(self.first_state_id)
        self._st_container.retrieve(self.first_state_id).enter()
        print('>>>pushin a state on the stack')

    def on_gameover(self, ev):
        self.gameover = True

    def on_state_change(self, ev):
        state_obj = self._st_container.retrieve(ev.state_ident)
        self._change_state(state_obj)

    def on_state_push(self, ev):
        state_obj = self._st_container.retrieve(ev.state_ident)
        self._push_state(state_obj)

    def on_state_pop(self, ev):
        self._pop_state()

    # --- helper func ----
    # deprecated
    def loop(self):
        """
        its forbidden to call .loop() in the web ctx, but its convenient in the local ctx
        if one wants to test a program without using the Kata VM
        :return:
        """
        # evsys3.create_manager()

        # lock mechanism, for extra safety so we never call .loop() in the web ctx
        print('*warning: never use .loop in the web ctx*')
        # use enter, update, exit to handle the global "run game logic"
        # self.enter()

        # notice: this class is "dirty" as it uses both the evsys4 and the evsys3
        # TODO cleanup
        # in evsys3 we had EngineEvTypes.GAMEBEGINS
        self.pev(events.EngineEvTypes.Gamestart)

        while not self.gameover:
            infot = time.time()
            self.pev(EngineEvTypes.Update, curr_t=infot)
            self.pev(EngineEvTypes.Paint, screen=vars.screen)

            self._manager.update()
            vscreen.flip()
            vars.clock.tick(vars.max_fps)
            # self.update(infot)
        # self.exit()
        # print(self.INFO_STOP_MSG)
        print('going out of the loop (StateStackCtrl)')


def declare_game_states(gs_enum, assoc_gscode_gscls):
    """
    :param gs_enum: enum of every single gamestate code
    :param assoc_gscode_gscls: a dict that binds a gamestate code to a gamestate class
    :param refgame: ref on the object whose type inherits from pyv.GameTpl
    """
    global stack_based_ctrl, multistate_flag

    multistate_flag = True
    stack_based_ctrl = StateStackCtrl(gs_enum, assoc_gscode_gscls)
    # activation Autho!
    stack_based_ctrl.turn_on()
