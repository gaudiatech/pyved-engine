import katagames_engine as kengi


_Listener = kengi.event2.EvListener


class BhCtrl(_Listener):
    def __init__(self, refview, gameref):
        super().__init__()
        self._v = refview
        self._g = gameref

    def _trigger_visual_change(self):
        self._v.curr_idx = (self._v.curr_idx + 1) % self._v.sprsheet_a.card
        self._v.curr_idx_b = (self._v.curr_idx_b + 1) % self._v.sprsheet_b.card

    def on_gamepad_dir(self, ev):
        print(ev.dir)

    def on_keydown(self, ev):
        self._trigger_visual_change()

    def on_gamepaddown(self, ev):
        print(ev.button)
        self._trigger_visual_change()

    def on_quit(self, ev):
        self._g.gameover = True


class BhView(_Listener):
    def __init__(self):
        super().__init__()
        self.sprsheet_a = kengi.gfx.Spritesheet('topdown-shooter-sprsheet.png')
        self.sprsheet_a.set_infos((32, 32))

        self.sprsheet_b = kengi.gfx.Spritesheet('topdown-shooter-sprsheet.png')
        self.sprsheet_b.set_infos((16, 16))
        self.curr_idx = self.curr_idx_b = 0

    def on_paint(self, ev):
        ev.screen.fill('orange')
        ev.screen.blit(self.sprsheet_a[self.curr_idx], (0, 0))
        ev.screen.blit(self.sprsheet_b[self.curr_idx_b], (48, 48))
