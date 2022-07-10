import katagames_engine as kengi
kengi.bootstrap_e()


# const
FPS_PBGE = 30

pygame = kengi.pygame  # alias to keep on using pygame, easily
screen = None
tilemap = tilemap2 = None
pbge = kengi.polarbear

isometric_maps = kengi.isometric


def get_maps():
    global tilemap, tilemap2
    return tilemap, tilemap2


class Character(isometric_maps.model.IsometricMapObject):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.surf = pygame.image.load("xassets/sys_icon.png").convert_alpha()
        # self.surf.set_colorkey((0,0,255))

    def __call__(self, dest_surface, sx, sy, mymap):
        mydest = self.surf.get_rect(midbottom=(sx, sy))
        dest_surface.blit(self.surf, mydest)


viewer = None
mypc = manager = paint_ev = mv_offset = None
keep_going = True
current_tilemap = 0


def game_init():
    global screen, tilemap, tilemap2, viewer, manager, mypc, paint_ev, mv_offset
    # aliases
    kengi.init(2)
    screen = kengi.core.get_screen()

    # model
    tilemap = isometric_maps.model.IsometricMap.load(['xassets', ], 'test_map.tmx')
    tilemap2 = isometric_maps.model.IsometricMap.load(['xassets', ], 'test_map2.tmx')
    mypc = Character(10.5, 10.5)
    list(tilemap.objectgroups.values())[0].contents.append(mypc)
    list(tilemap2.objectgroups.values())[0].contents.append(mypc)

    # view
    viewer = isometric_maps.IsometricMapViewer0(  # TODO unify
        tilemap, screen,
        up_scroll_key=pygame.K_UP,
        down_scroll_key=pygame.K_DOWN,
        left_scroll_key=pygame.K_LEFT,
        right_scroll_key=pygame.K_RIGHT
    )
    viewer.turn_on()

    cursor_image = pygame.image.load("xassets/half-floor-tile.png").convert_alpha()
    cursor_image.set_colorkey((255, 0, 255))
    viewer.cursor = isometric_maps.extras.IsometricMapQuarterCursor(0, 0, cursor_image, tilemap.layers[1])
    viewer.set_focused_object(mypc)

    # Chunk originally from PBGE. Also it sets key repeat freq.
    pygame.time.set_timer(pygame.USEREVENT, int(1000 / FPS_PBGE))
    pygame.key.set_repeat(200, 75)
    # TODO port Pbge to kengi CogObj+EventReceiver+event system,
    #  so we can avoid using pygame.USEREVENT and viewer() like here

    manager = kengi.event.EventManager.instance()
    CgmEvent = kengi.event.CgmEvent
    paint_ev = CgmEvent(kengi.event.EngineEvTypes.PAINT, screen=kengi.get_surface())
    mypc.x += 0.5
    mv_offset = 0.5


def game_update(infot=None):
    global manager, mypc, keep_going, current_tilemap
    keep_going = True

    while keep_going:

        gdi = pbge.wait_event()

        if gdi.type == pygame.QUIT:
            keep_going = False

        elif gdi.type == pygame.KEYDOWN:
            if gdi.key == pygame.K_ESCAPE:
                keep_going = False
            elif gdi.key == pygame.K_m:
                pass
                # mouse_x, mouse_y = pygame.mouse.get_pos()
                # print(
                #     viewer.map_x(mouse_x, mouse_y, return_int=False), viewer.map_y(mouse_x, mouse_y, return_int=False)
                # )
                # print(viewer.relative_x(0, 0), viewer.relative_y(0, 0))
                # print(viewer.relative_x(0, 19), viewer.relative_y(0, 19))
            elif gdi.key == pygame.K_RIGHT and mypc.x < tilemap.width - 1.5:
                mypc.x += mv_offset
            elif gdi.key == pygame.K_LEFT and mypc.x > -1:
                mypc.x -= mv_offset
            elif gdi.key == pygame.K_UP and mypc.y > -1:
                mypc.y -= mv_offset
            elif gdi.key == pygame.K_DOWN and mypc.y < tilemap.height - 1.5:
                mypc.y += mv_offset
            elif gdi.key == pygame.K_TAB:
                current_tilemap = 1 - current_tilemap
                viewer.switch_map(get_maps()[current_tilemap])

        # display
        manager.post(paint_ev)
        manager.update()
        kengi.flip()


if __name__ == '__main__':
    game_init()
    while keep_going:
        game_update()
    kengi.quit()