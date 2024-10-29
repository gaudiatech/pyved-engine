import pyved_engine as pyv


pyv.bootstrap_e()


class RpgActuator(pyv.EvListener):
    def __init__(self, refgame):
        super().__init__()
        self._game = refgame
        self._av_model = (
            pyv.rpg.Character('Erydram', level=13, maxhp=115, health=0.88, str=25, int=22, charisma=5, luck=3),
            pyv.rpg.Weapon('longsword', damage='2-9', req='str:8')
        )
        for obj in self._av_model:
            print(obj)
        self._opponent_model = (
            pyv.rpg.Character('Goblin', level=5, maxhp=100, str=8, int=1, charisma=2, luck=5),
        )
        print(self._opponent_model[0])

    def on_paint(self, ev):
        ev.screen.fill('antiquewhite2')
        pyv.flip()

    def on_quit(self, ev):
        self._game.gameover = True


class MyRpg(pyv.GameTpl):
    def get_video_mode(self):
        return pyv.LOW_RES_MODE

    def list_game_events(self):
        return None

    def enter(self, vms=None):
        super().enter(vms)
        RpgActuator(self).turn_on()


g = MyRpg()
g.loop()
