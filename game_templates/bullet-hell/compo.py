import bh_glvars as glvars
import katagames_engine as kengi


class MyView(kengi.event2.EvListener):
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

    def on_keydown(self, ev):
        self.curr_idx = (self.curr_idx+1) % self.sprsheet_a.card
        self.curr_idx_b = (self.curr_idx_b+1) % self.sprsheet_b.card

    def on_quit(self, ev):
        glvars.gameover = True
