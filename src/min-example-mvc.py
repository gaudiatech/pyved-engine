import katagames_engine as kengi
kengi.init('old_school')

pygame = kengi.pygame
EventReceiver = kengi.event.EventReceiver
EngineEvTypes = kengi.event.EngineEvTypes
scr_size = [0, 0]
curr_color_code = 0
acolors = {
    0: (244, 105, 251),
    1: (105, 184, 251)
}


class Avatar:
    def __init__(self):
        self.pos = [240, 135]
        self.direct = 0


class AvatarView(EventReceiver):
    def __init__(self, avref):
        super().__init__()
        self.avref = avref

    def proc_event(self, ev, source):
        if ev.type == EngineEvTypes.PAINT:
            ev.screen.fill(pygame.color.Color('antiquewhite2'))
            pygame.draw.circle(ev.screen, acolors[curr_color_code], self.avref.pos, 15, 0)


class AvatarCtrl(EventReceiver):
    def __init__(self, avref):
        super().__init__()
        self.avref = avref

    def proc_event(self, ev, source):
        global curr_color_code
        if ev.type == EngineEvTypes.LOGICUPDATE:
            avdir = self.avref.direct
            self.avref.pos[1] = (self.avref.pos[1] + avdir) % scr_size[1]
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_UP:
                self.avref.direct = -1
            elif ev.key == pygame.K_DOWN:
                self.avref.direct = 1
            elif ev.key == pygame.K_ESCAPE:
                self.pev(EngineEvTypes.GAMEENDS)
            elif ev.key == pygame.K_SPACE:
                curr_color_code = (curr_color_code + 1) % 2
        elif ev.type == pygame.KEYUP:
            prkeys = pygame.key.get_pressed()
            if not (prkeys[pygame.K_UP] or prkeys[pygame.K_DOWN]):
                self.avref.direct = 0


if __name__ == '__main__':
    game_scr = kengi.get_surface()
    scr_size[0], scr_size[1] = game_scr.get_size()
    av = Avatar()
    li_recv = [kengi.core.get_game_ctrl(), AvatarView(av), AvatarCtrl(av)]
    for recv_obj in li_recv:
        recv_obj.turn_on()
    li_recv[0].loop()
    kengi.quit()
