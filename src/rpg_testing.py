import katagames_engine as kengi

kengi.bootstrap_e()


class RpgActuator(kengi.EvListener):
    def __init__(self, refgame):
        super().__init__()
        self._game = refgame
        self._av_model = (
            kengi.rpg.Character('Erydram', level=13, maxhp=115, health=0.88, str=25, int=22, charisma=5, luck=3),
            kengi.rpg.Weapon('longsword', damage='2-9', req='str:8')
        )
        self._opponent_model = (
            kengi.rpg.Character('Goblin', level=5, maxhp=100, str=8, int=1, charisma=2, luck=5)
        )

    def on_paint(self, ev):
        ev.screen.fill('antiquewhite2')
        kengi.flip()

    def on_quit(self, ev):
        self._game.gameover = True


class MyRpg(kengi.GameTpl):
    def init_video(self):
        kengi.init(2)

    def enter(self, vms=None):
        super().enter(vms)
        RpgActuator(self).turn_on()


g = MyRpg()
g.loop()
