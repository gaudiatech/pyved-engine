import json
import random

from .shared_code import glvars
from .shared_code.NetwReadyModel import NetwReadyModel


class Server:
    def __init__(self, **kwargs):
        print('object Server received:', kwargs)
        self._model = NetwReadyModel(None)
        self.mediator = glvars.mediator

        self.mediator.register('player_moves', self.on_player_moves)
        self.mediator.register('x_request_sync', self.on_x_request_sync)
        self.mediator.register('x_client_spawns', self.on_x_client_spawns)
        self.mediator.register('x_request_movement', self.on_x_request_movement)

        self._empty_world = True  # when no player has ever logged in, this is True
        self._t_last_ai_move = None

    def disp_model(self):
        """
        displays the world in a text/ASCII fashion. Used only for debug
        """
        self._model.display()

    def proc_server_logic(self, info_t):
        if self._empty_world:
            return
        if self._t_last_ai_move is None:
            self._t_last_ai_move = info_t
            return
        # cas général
        dt = (info_t - self._t_last_ai_move)
        if dt > 3.0:
            omega = self._model.get_possible_mvt('ai')
            if len(omega) > 0:
                if len(omega) == 1:
                    choice = omega[0]
                else:
                    choice = random.choice(omega)
                self._model.move_pl('ai', choice)
                self._t_last_ai_move = info_t

    # ---------------
    # callbacks
    # ---------------
    def _do_force_clients_sync(self):
        self._model.pev('x_notify_new_state', self._model.serialize())

    def on_player_moves(self, event):
        # its a regular event therefore the model has been updated locally, server-side
        self._do_force_clients_sync()

    def on_x_request_sync(self, event):
        self._empty_world = False
        self._do_force_clients_sync()

    def on_x_client_spawns(self, event):
        pass

    def on_x_request_movement(self, event):
        print('reception on_x_request_movement par server', event)
        lp, i_str, j_str = json.loads(event)
        i, j = map(int, (i_str, j_str))
        self._model.move_pl(lp, (i, j))
        self._do_force_clients_sync()
