"""
Game template - Bullet Hell

Assets created by Dyru, license CC BY 4.0, https://www.instagram.com/art_by_dyru/
"""
import katagames_engine as kengi
from compo import BhCtrl, BhView


class BhGame(kengi.GameTpl):
    def __init__(self):
        super().__init__()
        self.g_compo = list()

    # redefine
    def enter(self, vms=None):
        kengi.init(2, 'bullet hell example')
        self._manager = kengi.get_ev_manager()
        self._manager.setup()

        v = BhView()
        self.g_compo.extend((
            v,
            BhCtrl(v, self)
        ))
        for c in self.g_compo:
            c.turn_on()


game_obj = BhGame()  # ->standard variable name (game_obj)


if __name__ == '__main__':  # run game (local context)
    game_obj.enter()
    while not game_obj.gameover:
        game_obj.update(0)
    game_obj.exit()
    print('Clean exit-')
