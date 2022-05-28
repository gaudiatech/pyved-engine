import sys

import katagames_engine as kengi

kengi.init('old_school')  # instead of pygame.init(), and pygame.display.set_mode(...)

pygame = kengi.pygame  # alias to keep on using pygame, easily
screen = kengi.core.get_screen()  # new way to retrieve the surface used for display

#pbge = kengi.polarbear
#pbge.init()

import isometric_maps

import demolib

tilemap = isometric_maps.IsometricMap.load('assets/test_map.tmx')
tilemap2 = isometric_maps.IsometricMap.load('assets/test_map2.tmx')

maps = (tilemap, tilemap2)

viewer = kengi.isometric.IsometricMapViewer(tilemap, screen, up_scroll_key=pygame.K_UP,
                                               down_scroll_key=pygame.K_DOWN, left_scroll_key=pygame.K_LEFT,
                                               right_scroll_key=pygame.K_RIGHT)
cursor_image = pygame.image.load("assets/half-floor-tile.png").convert_alpha()
cursor_image.set_colorkey((255, 0, 255))
viewer.cursor = isometric_maps.IsometricMapQuarterCursor(0, 0, cursor_image, tilemap.layers[1])




class Character(isometric_maps.IsometricMapObject):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.surf = pygame.image.load("assets/sys_icon.png").convert_alpha()
        # self.surf.set_colorkey((0,0,255))

    def __call__(self, dest_surface, sx, sy, mymap):
        mydest = self.surf.get_rect(midbottom=(sx, sy))
        dest_surface.blit(self.surf, mydest)


class NPC(isometric_maps.IsometricMapObject):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.surf = pygame.image.load("assets/npc.png").convert_alpha()
        # self.surf.set_colorkey((0,0,255))

    def __call__(self, dest_surface, sx, sy, mymap):
        mydest = self.surf.get_rect(midbottom=(sx, sy))
        dest_surface.blit(self.surf, mydest)


class MovementPath():
    def __init__(self, mapob, dest, mymap):
        #print(dest)
        self.mapob = mapob
        self.dest = dest
        self.goal = None
        blocked_tiles = set()
        obgroup = list(mymap.objectgroups.values())[0]
        for ob in obgroup.contents:
            if ob is not mapob:
                blocked_tiles.add((ob.x,ob.y))
                if self.pos_to_index((ob.x, ob.y)) == self.pos_to_index(dest):
                    self.goal = ob
        self.path = demolib.pathfinding.AStarPath(mymap, self.pos_to_index((mapob.x, mapob.y)), self.pos_to_index(dest), self.tile_is_blocked, blocked_tiles)
        if self.path.results:
            self.path.results.pop(0)
        self.all_the_way_to_dest = not (dest in blocked_tiles or self.tile_is_blocked(mymap, *self.pos_to_index(dest)))
        if self.path.results and not self.all_the_way_to_dest:
            self.path.results.pop(-1)
        self.animob = None

    @staticmethod
    def pos_to_index(pos):
        x = int(pos[0] + 0.99)
        y = int(pos[1] + 0.99)
        return x,y

    @staticmethod
    def tile_is_blocked(mymap, x, y):
        return not(mymap.on_the_map(x,y) and mymap.layers[1][x,y] == 0)

    def __call__(self):
        # Called once per update; returns True when the action is completed.
        if self.animob:
            self.animob.update()
            if self.animob.needs_deletion:
                self.animob = None
        if not self.animob:
            if self.path.results:
                if len(self.path.results) == 1 and self.all_the_way_to_dest:
                    nugoal = self.dest
                    self.path.results = []
                else:
                    nugoal = self.path.results.pop(0)
                self.animob = demolib.animobs.MoveModel(self.mapob, start=(self.mapob.x,self.mapob.y), dest=nugoal, speed=0.25)
            else:
                #print((self.mapob.x,self.mapob.y))
                #sx, sy = viewer.screen_coords(self.mapob.x, self.mapob.y, 0, -8)
                #print(viewer.map_x(sx, sy, return_int=False), viewer.map_y(sx, sy, return_int=False))
                return True


myviewer = None


def start_conversation():
    global myviewer
    myconvo = demolib.dialogue.Offer.load_json("assets/conversation.json")
    myviewer = demolib.dialogue.SimpleVisualizer(myconvo, viewer)
    myviewer.converse()


mypc = Character(10, 10)
mynpc = NPC(15,15)
list(tilemap.objectgroups.values())[0].contents.append(mypc)
list(tilemap2.objectgroups.values())[0].contents.append(mypc)
list(tilemap.objectgroups.values())[0].contents.append(mynpc)
list(tilemap2.objectgroups.values())[0].contents.append(mynpc)

viewer.set_focused_object(mypc)
viewer.turn_on()
# force: center on avatar op.
mypc.x += 0.5

manager = kengi.event.EventManager.instance()
CgmEvent = kengi.event.CgmEvent
EngineEvTypes = kengi.event.EngineEvTypes
paint_ev = CgmEvent(EngineEvTypes.PAINT, screen=kengi.get_surface())
lu_ev = CgmEvent(EngineEvTypes.LOGICUPDATE, curr_t=None)

keep_going = True
current_tilemap = 0
current_path = None


class PathCtrl(kengi.event.EventReceiver):
    def __init__(self):
        super().__init__()

    def proc_event(self, event, source):
        global current_path
        if event.type == EngineEvTypes.LOGICUPDATE:
            if current_path is not None:
                ending_reached = current_path()
                if ending_reached:
                    if current_path.goal:
                        print('DEBUT DIALOGUE')
                        start_conversation()
                    current_path = None


class DialogueView(kengi.event.EventReceiver):
    def __init__(self):
        super().__init__()

    def proc_event(self, event, source):
        global myviewer
        if myviewer is not None:
            if event.type == EngineEvTypes.PAINT:
                myviewer.render()


dview = DialogueView()
dview.turn_on()

pctrl = PathCtrl()
pctrl.turn_on()
clock = pygame.time.Clock()


class BasicCtrl(kengi.event.EventReceiver):
    def proc_event(self, gdi, source):
        global keep_going, current_tilemap, current_path

        if gdi.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONUP):
            cursor = viewer.cursor
            if cursor:
                cursor.update(viewer, gdi)
            if gdi.type == pygame.MOUSEBUTTONUP and gdi.button == 1:
                print('movement path set')
                current_path = MovementPath(mypc, viewer.cursor.get_pos(), maps[current_tilemap])

        elif gdi.type == pygame.KEYDOWN:
            if gdi.key == pygame.K_ESCAPE:
                keep_going = False
            elif gdi.key == pygame.K_m:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                print(viewer.map_x(mouse_x, mouse_y, return_int=False), viewer.map_y(mouse_x, mouse_y, return_int=False))
                print(viewer.relative_x(0, 0), viewer.relative_y(0, 0))
                print(viewer.relative_x(0, 19), viewer.relative_y(0, 19))
            elif gdi.key == pygame.K_d and mypc.x < tilemap.width - 1.5:
                mypc.x += 0.1
            elif gdi.key == pygame.K_a and mypc.x > -1:
                mypc.x -= 0.1
            elif gdi.key == pygame.K_w and mypc.y > -1:
                mypc.y -= 0.1
            elif gdi.key == pygame.K_s and mypc.y < tilemap.height - 1.5:
                mypc.y += 0.1
            elif gdi.key == pygame.K_TAB:
                current_tilemap = 1 - current_tilemap
                viewer.switch_map(maps[current_tilemap])

        elif gdi.type == pygame.QUIT:
            keep_going = False


bctrl = BasicCtrl()
bctrl.turn_on()

while keep_going:
    # gdi = kengi.polarbear.wait_event()
    #for ev in pygame.event.get():
    #    handle_event(ev)
    #viewer.check_event(gdi)

    # display
    manager.post(lu_ev)
    # so pbge works properly
    pygame.event.post(pygame.event.Event(pygame.USEREVENT))

    manager.post(paint_ev)
    manager.update()

    kengi.flip()
    clock.tick(60)


kengi.quit()  # instead of pygame.quit()
