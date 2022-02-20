import katagames_sdk.engine as kataen

pygame = kataen.pygame
EventReceiver = kataen.event.EventReceiver
EngineEvTypes = kataen.event.EngineEvTypes
scr_size = [0, 0]


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
            pygame.draw.circle(ev.screen, (244, 105, 251), self.avref.pos, 15, 0)


class AvatarCtrl(EventReceiver):
    def __init__(self, avref):
        super().__init__()
        self.avref = avref

    def proc_event(self, ev, source):
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
        elif ev.type == pygame.KEYUP:
            prkeys = pygame.key.get_pressed()
            if not (prkeys[pygame.K_UP] or prkeys[pygame.K_DOWN]):
                self.avref.direct = 0


if __name__ == '__main__':
    kataen.core.init('old_school')
    game_scr = kataen.core.get_screen()
    scr_size[0], scr_size[1] = game_scr.get_size()
    av = Avatar()
    li_recv = [kataen.core.get_game_ctrl(), AvatarView(av), AvatarCtrl(av)]
    for recv_obj in li_recv:
        recv_obj.turn_on()
    li_recv[0].loop()
    kataen.core.cleanup()
