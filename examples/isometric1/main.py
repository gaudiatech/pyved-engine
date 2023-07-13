import pyved_engine as pyv

pyv.bootstrap_e()


# TODO need to unify this! You should use what is already in pyv.*
import demolib.animobs as animobs
import demolib.dialogue as dialogue
import demolib.pathfinding as pathfinding
from demolib.defs import MyEvTypes
import math


# will polarbear crash the game if this line isnt added, after pyv.init?
# pyv.polarbear.my_state.screen = pyv.get_surface()

# - aliases
pygame = pyv.pygame  # alias to keep on using pygame, easily
EngineEvTypes = pyv.EngineEvTypes

# global variables
conv_viewer = None
conversation_ongoing = False
current_path = None
current_tilemap = 0
maps = list()
map_viewer = None
mypc = mynpc = None
path_ctrl = None
screen = None
tilemap_height = tilemap_width = 0


class Character(pyv.isometric.model.IsometricMapObject):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.surf = pygame.image.load("assets/sys_icon.png").convert_alpha()
        # self.surf.set_colorkey((0,0,255))

    def __call__(self, dest_surface, sx, sy, mymap):
        mydest = self.surf.get_rect(midbottom=(sx, sy))
        dest_surface.blit(self.surf, mydest)


class MovementPath:
    def __init__(self, mapob, dest, mymap):
        self.mapob = mapob
        self.dest = dest
        self.goal = None
        self.mymap = mymap
        self.blocked_tiles = set()
        obgroup = list(mymap.objectgroups.values())[0]
        for ob in obgroup.contents:
            if ob is not mapob:
                self.blocked_tiles.add((ob.x, ob.y))
                if self.pos_to_index((ob.x, ob.y)) == self.pos_to_index(dest):
                    self.goal = ob
        self.path = pathfinding.AStarPath(
            mymap, self.pos_to_index((mapob.x, mapob.y)), self.pos_to_index(dest), self.tile_is_blocked,
            mymap.clamp_pos_int, blocked_tiles=self.blocked_tiles
        )
        if not self.path.results:
            print("No path found!")
        if self.path.results:
            self.path.results.pop(0)
        self.all_the_way_to_dest = not (
                    dest in self.blocked_tiles or self.tile_is_blocked(mymap, *self.pos_to_index(dest)))
        if self.path.results and not self.all_the_way_to_dest:
            self.path.results.pop(-1)
        self.animob = None

    @staticmethod
    def pos_to_index(pos):
        x = math.floor(pos[0])
        y = math.floor(pos[1])
        return x, y

    @staticmethod
    def tile_is_blocked(mymap, x, y):
        return mymap.tile_is_blocked(x, y)

    def __call__(self):
        # Called once per update; returns True when the action is completed.
        if self.animob:
            self.animob.update()
            if self.animob.needs_deletion:
                self.animob = None
        if not self.animob:
            if self.path.results:
                if len(self.path.results) == 1 and self.all_the_way_to_dest:
                    nx, ny = self.dest
                    self.path.results = []
                else:
                    nx, ny = self.path.results.pop(0)

                # De-clamp the nugoal coordinates.
                nx = min([nx, nx - self.mymap.width, nx + self.mymap.width], key=lambda x: abs(x - self.mapob.x))
                ny = min([ny, ny - self.mymap.height, ny + self.mymap.height], key=lambda y: abs(y - self.mapob.y))

                self.animob = animobs.MoveModel(
                    self.mapob, dest=(nx, ny), speed=0.25
                )
            else:
                # print((self.mapob.x,self.mapob.y))
                # sx, sy = viewer.screen_coords(self.mapob.x, self.mapob.y, 0, -8)
                # print(viewer.map_x(sx, sy, return_int=False), viewer.map_y(sx, sy, return_int=False))
                return True


class NPC(pyv.isometric.model.IsometricMapObject):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.surf = pygame.image.load("assets/npc.png").convert_alpha()
        # self.surf.set_colorkey((0,0,255))

    def __call__(self, dest_surface, sx, sy, mymap):
        mydest = self.surf.get_rect(midbottom=(sx, sy))
        dest_surface.blit(self.surf, mydest)


# --------------------------------------------
# Define controllers etc
# --------------------------------------------
class BasicCtrl(pyv.EvListener):

    def _proc_mouse_ev(self, ev):
        global mypc, map_viewer, current_path
        if ev.type == EngineEvTypes.Mouseup:
            current_path = MovementPath(mypc, map_viewer.cursor.get_pos(), maps[current_tilemap])
            print('movement path has been set', current_path)

    def on_mouseup(self, gdi):
        global map_viewer
        if conversation_ongoing:
            pass  # block all movement when the conversation is active
        else:
            cursor = map_viewer.cursor
            if cursor:
                cursor.update(map_viewer, gdi)
            self._proc_mouse_ev(gdi)

    # def proc_event(self, gdi):
    #     global conversation_ongoing, map_viewer, mypc, current_tilemap, current_path
    #     if gdi.type == pygame.KEYDOWN:
    #         if gdi.key == pygame.K_ESCAPE:
    #             if conversation_ongoing:
    #                 # abort
    #                 self.pev(MyEvTypes.ConvEnds)
    #             else:
    #                 self.pev(EngineEvTypes.GAMEENDS)
    #         elif gdi.key == pygame.K_d and mypc.x < tilemap_width - 1.5:
    #             mypc.x += 0.1
    #         elif gdi.key == pygame.K_a and mypc.x > -1:
    #             mypc.x -= 0.1
    #         elif gdi.key == pygame.K_w and mypc.y > -1:
    #             mypc.y -= 0.1
    #         elif gdi.key == pygame.K_s and mypc.y < tilemap_height - 1.5:
    #             mypc.y += 0.1
    #         elif gdi.key == pygame.K_TAB:
    #             current_tilemap = 1 - current_tilemap
    #             map_viewer.switch_map(maps[current_tilemap])


class PathCtrl(pyv.EvListener):
    def __init__(self):
        super().__init__()

    def on_event(self, event):
        global current_path, conv_viewer, conversation_ongoing

        if event.type == EngineEvTypes.Update:
            if current_path is not None:
                ending_reached = current_path()
                if ending_reached:
                    if current_path.goal:
                        conversation_ongoing = True
                        myconvo = dialogue.Offer.load_json("assets/conversation.json")
                        conv_viewer = dialogue.ConversationView(myconvo)
                        conv_viewer.turn_on()
                    current_path = None

        elif event.type == MyEvTypes.ConvEnds:
            conversation_ongoing = False  # unlock player movements
            if conv_viewer.active:
                conv_viewer.turn_off()


def _load_maps():
    global maps, tilemap_width, tilemap_height
    maps.append(
        pyv.isometric.model.IsometricMap.load(['assets', ], 'test_map.tmx')
    )
    maps.append(
        pyv.isometric.model.IsometricMap.load(['assets', ], 'test_map2.tmx')
    )
    tilemap_width, tilemap_height = maps[0].width, maps[0].height


def _add_map_entities(gviewer):
    global mypc, mynpc
    mypc = Character(10, 10)
    mynpc = NPC(15, 15)
    tm, tm2 = maps[0], maps[1]
    list(tm.objectgroups.values())[0].contents.append(mypc)
    list(tm2.objectgroups.values())[0].contents.append(mypc)

    list(tm.objectgroups.values())[0].contents.append(mynpc)
    list(tm2.objectgroups.values())[0].contents.append(mynpc)

    gviewer.set_focused_object(mypc)
    # force: center on avatar op.
    # mypc.x += 0.5


def _init_specific_stuff():
    global map_viewer, maps

    _load_maps()
    map_viewer = pyv.isometric.IsometricMapViewer(  # TODO unify
        maps[0], screen,
        up_scroll_key=pygame.K_UP, down_scroll_key=pygame.K_DOWN,
        left_scroll_key=pygame.K_LEFT, right_scroll_key=pygame.K_RIGHT
    )
    _add_map_entities(map_viewer)

    cursor_image = pygame.image.load("assets/half-floor-tile.png").convert_alpha()
    cursor_image.set_colorkey((255, 0, 255))
    map_viewer.cursor = pyv.isometric.extras.IsometricMapQuarterCursor(0, 0, cursor_image, maps[0].layers[1])

    pctrl = PathCtrl()
    map_viewer.turn_on()
    pctrl.turn_on()

    bctrl = BasicCtrl()
    bctrl.turn_on()


if __name__ == '__main__':
    pyv.init(2)
    screen = pyv.get_surface()  # retrieve the surface used for display

    emg = pyv.get_ev_manager()
    emg.setup()

    _init_specific_stuff()

    gctrl = pyv.get_game_ctrl()
    gctrl.turn_on()
    gctrl.loop()

    pyv.quit()
    print('bye!')
