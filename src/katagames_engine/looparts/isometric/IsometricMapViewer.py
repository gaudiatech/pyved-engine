import math

from .isosm_config import NOT_ALL_FLAGS, FLIPPED_VERTICALLY_FLAG, FLIPPED_HORIZONTALLY_FLAG, SCROLL_STEP
from ... import _hub
from ...compo import vscreen as core


# - aliases
EngineEvTypes = _hub.events.EngineEvTypes
EvListener = _hub.events.EvListener

# --------------------------------------------
# optimization
_gl_halftile_w = _gl_halftile_h = None
_buffer_relx = dict()
_buffer_rely = dict()


def relative_x(x, y):
    """Return the relative x position of this tile, ignoring offset."""
    try:
        return _buffer_relx[x][y]
    except KeyError:
        if x not in _buffer_relx:
            _buffer_relx[x] = dict()
        _buffer_relx[x][y] = int(x * _gl_halftile_w - y * _gl_halftile_w)
        return _buffer_relx[x][y]


def relative_y(x, y):
    """Return the relative y position of this tile, ignoring offset."""
    try:
        return _buffer_rely[x][y]
    except KeyError:
        if x not in _buffer_rely:
            _buffer_rely[x] = dict()
        _buffer_rely[x][y] = int(y * _gl_halftile_h + x * _gl_halftile_h)
        return _buffer_rely[x][y]


def rel_set_info(halftile_w, halftile_h):
    global _gl_halftile_w, _gl_halftile_h, _buffer_relx, _buffer_rely
    _gl_halftile_w = float(halftile_w)
    _gl_halftile_h = float(halftile_h)
    _buffer_relx.clear()
    _buffer_rely.clear()


# ----------------------------------------------


class IsometricMapViewer(EvListener):
    MEGAOPTIM = False
    SOLID_COLOR = 'navyblue'
    FLOORS = {}
    FLOOR_MAN_OFFSET = {
        0: (1617 + 305, 240 - 128),  # what offset one needs to apply so the floor img is aligned, map 0 (city.png)
        1: (522 + 300, 100 - 92)
    }
    UPINK = (255, 0, 255)

    @property
    def show_avatar(self):
        return self._show_avatar

    @show_avatar.setter
    def show_avatar(self, newval):
        self._show_avatar = newval
        self.force_redraw_flag = True

    def set_av_anim_speed(self, v):
        self.av_phase_thresh = int(100/v)

    def __init__(self, isometric_map, screen, postfx=None, cursor=None,
                 left_scroll_key=None, right_scroll_key=None, up_scroll_key=None, down_scroll_key=None):
        super().__init__()

        # RELATED to avatar {{ -- player character class --
        self.pc_cls = int  # this needs to be set from outside, related to perf optimization
        self._show_avatar = True
        self.force_redraw_flag = False
        self.av_phase_thresh = 3
        self.av_phase = self.av_phase_thresh - 1
        self.av_frame = 1
        self.anim_av_offset = [2.0, -1.0]
        self.cutav = None
        self.cutav_cpt = 1

        self.extra_anim = None
        # done }}
        self.animated_wallpaper = False
        self.block_wallpaper = False
        self.info_draw_mapobj = dict()

        self.isometric_map = isometric_map

        self.manoffset = (0, 0)
        self.scrollable_floor = None

        self.screen = screen
        self.mid = (
            self.screen.get_width() // 2, self.screen.get_height() // 2
        )
        # self.prevx = float('NaN')
        # self.prevy = float('NaN')

        self.floor_rect = _hub.pygame.Rect(0, 0, self.screen.get_width(), self.screen.get_height())
        self.gfx_data_buffer = _hub.pygame.Surface(self.screen.get_size())
        self.gfx_data_buffer.set_colorkey(self.UPINK)

        if isometric_map.wallpaper:
            self.screen_rect = self.screen.get_rect()
            wp_width, wp_height = self.isometric_map.wallpaper.get_size()
            self.wp_temp_rect = _hub.pygame.Rect(0, 0, wp_width, wp_height)
            self.wp_grid_w = self.screen_rect.w // wp_width + 1
            self.wp_grid_h = self.screen_rect.h // wp_height + 1

        # The focus is defined by map coordinates, so a lot of the back and forth between screen and map coords
        # can be cut.
        self._focus_x = 0
        self._focus_y = 0
        self._focused_object_x0 = 0
        self._focused_object_y0 = 0
        self._focused_object = None

        self.phase = 0

        self.tile_width = isometric_map.tile_width
        self.tile_height = isometric_map.tile_height

        self.half_tile_width = isometric_map.tile_width // 2
        self.half_tile_height = isometric_map.tile_height // 2
        rel_set_info(
            self.half_tile_width, self.half_tile_height
        )
        self.visible_area = None
        self._init_visible_area_init(self.screen)

        # _mouse_tile contains the actual tile the mouse is hovering over. However, in most cases what we really want
        # is the location of the mouse cursor. Time to make a property!
        self._mouse_tile = (-1, -1)
        self.postfx = postfx
        self.cursor = cursor
        self.left_scroll_key = left_scroll_key
        self.right_scroll_key = right_scroll_key
        self.up_scroll_key = up_scroll_key
        self.down_scroll_key = down_scroll_key
        self.debug_sprite = None
        self.lastmousepos = None

        # util for the drawing of tiles
        self.line_cache = list()
        self.objgroup_contents = dict()
        self.objgroup_modified_mappos = dict()
        self._camera_updated_this_frame = False

    def enable_megaoptim(self, imgcity, imgcasino):
        self.MEGAOPTIM = True
        self.FLOORS.update({
            0: imgcity,
            1: imgcasino
        })
        self.manoffset = self.FLOOR_MAN_OFFSET[0]
        self.scrollable_floor = self.FLOORS[0]
        self.scrollable_floor.set_colorkey(self.UPINK)

    def _check_mouse_scroll(self, screen_area, mouse_x, mouse_y):
        # Check for map scrolling, depending on mouse position.
        if not self._camera_updated_this_frame:
            if mouse_x < 20:
                dx = -SCROLL_STEP
            elif mouse_x > (screen_area.right - 20):
                dx = +SCROLL_STEP
            else:
                dx = 0

            if mouse_y < 20:
                dy = -SCROLL_STEP
            elif mouse_y > (screen_area.bottom - 20):
                dy = +SCROLL_STEP
            else:
                dy = 0

            if dx or dy:
                self._update_camera(dx, dy)

    def _get_horizontal_line(self, x0, y0, line_number):
        x = x0 + line_number // 2
        y = y0 + (line_number + 1) // 2

        _, py = self.screen_coords(x, y)
        if py > self.visible_area.bottom:
            return None

        mylist = list()
        while self.screen_coords(x, y)[0] < self.visible_area.right:
            if self.isometric_map.on_the_map(x, y):
                mylist.append((x, y))
            x += 1
            y -= 1
        return mylist

    def _init_visible_area_init(self, scr):
        # The visible area describes the region of the map we need to draw
        w, h = scr.get_size()
        # below: args idx 0 and 1 do not matter actually
        tw, th = self.isometric_map.tile_width, self.isometric_map.tile_height
        self.visible_area = _hub.pygame.Rect(0, 0, w + int(0.5*tw), h + 6*th)

    def _model_depth(self, model):
        return relative_y(model.x, model.y)

    def _update_camera(self, dx, dy):
        # If the mouse and the arrow keys conflict, only one of them should win.
        if self._camera_updated_this_frame:
            return
        self._focus_x, self._focus_y = self.isometric_map.clamp_pos([self._focus_x + dx, self._focus_y + dy])

    def impacte_surf(self, output_surf):
        # --- init step before drawing map objects:
        # we record all of the objectgroup contents for display when their tile comes up
        # Also, clamp all object positions. If this is an infinite scrolling map,
        # objects can move off one side to the map to the other.
        # However, in their data, we want the objects to stay within the bounds of the map.

        # ++++++ old code:
        # print( self.isometric_map.objectgroups.keys() )
        # print(self.isometric_map.objectgroups.values())
        # for k, v in self.isometric_map.objectgroups.items():
        #     self.objgroup_contents[k] = collections.defaultdict(list)
        #     for ob in v.contents:
        #         print('ob found:', ob)
        #         ob.x, ob.y = self.isometric_map.clamp_pos((ob.x, ob.y))
        #         sx, sy = self.screen_coords(ob.x, ob.y, v.offsetx, v.offsety)
        #         mx, my = self.map_x(sx, sy, return_int=False), self.map_y(sx, sy, return_int=False)
        #         obkey = self.isometric_map.clamp_pos_int((mx, my))
        #         self.objgroup_contents[k][obkey].append(ob)
        #         # Also save the mofidied map pos, which will come in handy later.
        #         self.objgroup_modified_mappos[ob] = (mx, my)
        # print(3 / 0)

        # ++++++ new code:
        self.info_draw_mapobj.clear()
        for layerk, objgroup in self.isometric_map.objectgroups.items():
            offx, offy = objgroup.offsetx, objgroup.offsety
            for map_obj in objgroup.contents:
                # cas spe:
                if type(map_obj) == self.pc_cls:
                    ob = map_obj
                    ob.x, ob.y = self.isometric_map.clamp_pos((ob.x, ob.y))  # mini-tp player!
                    sx, sy = self.screen_coords(ob.x, ob.y, objgroup.offsetx, objgroup.offsety)
                    mx, my = self.map_x(sx, sy, return_int=False), self.map_y(sx, sy, return_int=False)
                    obkey = self.isometric_map.clamp_pos_int((mx, my))
                    self.objgroup_contents[layerk] = dict()
                    self.objgroup_contents[layerk][obkey] = [ob]
                    self.objgroup_modified_mappos[ob] = (mx, my)
                    continue
                # cas général
                scrx, scry = self.screen_coords(map_obj.x, map_obj.y, offx, offy)
                if 0 <= scrx < self.floor_rect.w+self.isometric_map.tile_width:
                    if 0 <= scry < self.floor_rect.h:
                        # info_mapobj_k = self.isometric_map.clamp_pos_int((map_obj.x+offx, map_obj.y+offy))
                        self.info_draw_mapobj[map_obj] = (scrx, scry)  # rule: 1 map_obj per location!
                        # save the mofidied map pos, which will come in handy later.
                        # self.objgroup_modified_mappos[map_obj] = (scrx, scry)

            # STOP the loop right now! Because,
            # actually we use only one value of the dict,
            # since all map objects are def. in the same layer
            break
        # ---

        x, y = self.map_x(0, 0) - 2, self.map_y(0, 0) - 1
        x0, y0 = x, y
        painting_tiles = True
        line_number = 1

        while painting_tiles:
            # In order to allow smooth sub-tile movement of stuff, we have
            # to draw everything in a particular order.
            nuline = self._get_horizontal_line(x0, y0, line_number)
            self.line_cache.append(nuline)
            current_y_offset = self.isometric_map.layers[0].offsety
            current_line = len(self.line_cache) - 1

            for layer_num, layer in enumerate(self.isometric_map.layers):
                # ------------------------------------- check this out <<<
                # --- OPTIM blit large image for the ground level (3/3)---
                if self.MEGAOPTIM:
                    if layer_num == 0:
                        continue

                if current_line >= 0:

                    # - Tom N.B.
                    # this was a chunk of code that draws object. I dont think its very efficient so i replace it,
                    # see {NEW CHUNK OBJ DRAW} that uses: self. info_draw_mapobj

                    # if current_line > 1 and layer in self.objgroup_contents and self.line_cache[current_line - 1]:
                    #     # After drawing the terrain last time, draw any objects in the previous cell.
                    #     for x, y in self.line_cache[current_line - 1]:
                    #         if self.cursor:
                    #             if self.cursor.layer_name == layer.name and x == self.cursor.x and y == self.cursor.y:
                    #                 self.cursor.render(self)
                    #
                    #         ox, oy = x % self.isometric_map.width, y % self.isometric_map.height
                    #         if (ox, oy) in self.objgroup_contents[layer]:
                    #             self.objgroup_contents[layer][(ox, oy)].sort(key=self._model_depth)
                    #             for ob in self.objgroup_contents[layer][(ox, oy)]:
                    #                 # The following bit of math makes sure that the clamped object positions will
                    #                 # print at the correct screen positions. Otherwise, if the player/focus is on the
                    #                 # other side of the map seam, this object will be printed in the wrong position.
                    #                 mmx, mmy = self.objgroup_modified_mappos[ob]
                    #                 fx = x + math.modf(mmx)[0]
                    #                 fy = y + math.modf(mmy)[0]
                    #                 sx, sy = self.screen_coords(
                    #                     fx, fy,
                    #                     self.isometric_map.objectgroups[layer].offsetx,
                    #                     self.isometric_map.objectgroups[layer].offsety
                    #                 )
                    #                 ob(output_surf, sx, sy, self.isometric_map)

                    # player draw( 1)
                    if self._show_avatar:  # otherwise, the avatar is invisble!
                        if current_line > 1 and layer in self.objgroup_contents and self.line_cache[current_line - 1]:
                            for x, y in self.line_cache[current_line - 1]:
                                ox, oy = x % self.isometric_map.width, y % self.isometric_map.height
                                if (ox, oy) in self.objgroup_contents[layer]:
                                    # @@@ nothing to sort bc we have only the player here!@@@
                                    # self.objgroup_contents[layer][(ox, oy)].sort(key=self._model_depth)
                                    for ob in self.objgroup_contents[layer][(ox, oy)]:
                                        mmx, mmy = self.objgroup_modified_mappos[ob]
                                        fx = x + math.modf(mmx)[0]
                                        fy = y + math.modf(mmy)[0]
                                        sx, sy = self.screen_coords(
                                            fx, fy,
                                            self.isometric_map.objectgroups[layer].offsetx,
                                            self.isometric_map.objectgroups[layer].offsety
                                        )
                                        ob(output_surf, sx, sy, self.isometric_map)

                    # - the rest of the drawing algorithm
                    if self.line_cache[current_line]:
                        for x, y in self.line_cache[current_line]:
                            gid = layer[x, y]
                            tile_id = gid & NOT_ALL_FLAGS
                            if tile_id > 0:
                                my_tile = self.isometric_map.tilesets[tile_id]
                                # Note that x,y refer to IsometricMapObject coordinates, and so 0,0 points at the
                                # top of the "ground" level of a tile. So, we adjust sy before sending the coords
                                # to the printer, so it is pointing at the bottom corner of the tile instead.
                                sx, sy = self.screen_coords(x, y)
                                my_tile.paint_tile(
                                    output_surf, sx, sy + layer.offsety + self.isometric_map.tile_height,
                                                     gid & FLIPPED_HORIZONTALLY_FLAG,
                                                     gid & FLIPPED_VERTICALLY_FLAG)

                    elif self.line_cache[current_line] is None:  # and layer == self.isometric_map.layers[-1]:
                        painting_tiles = False
                else:
                    break
                if layer.offsety < current_y_offset:
                    current_line -= 1
                    current_y_offset = layer.offsety
            line_number += 1

        self.phase = (self.phase + 1) % 640
        del self.line_cache[:]
        self.objgroup_contents.clear()
        self.objgroup_modified_mappos.clear()
        # fin impacte_surf

    def fill_wallpaper(self):
        for x in range(-1, self.wp_grid_w):
            self.wp_temp_rect.x = self.screen_rect.x + x * self.wp_temp_rect.w
            for y in range(-1, self.wp_grid_h):
                self.wp_temp_rect.y = self.screen_rect.y + y * self.wp_temp_rect.h
                if self.animated_wallpaper:
                    self.wp_temp_rect.y += self.phase

                self.screen.blit(self.isometric_map.wallpaper, self.wp_temp_rect)

    def focus(self, x, y):
        """Move the camera to point at the requested map tile. x,y can be ints or floats."""
        self._focus_x, self._focus_y = self.isometric_map.clamp_pos((x, y))

        # self.floor_rect.x = a
        # self.floor_rect.y = b

    def map_x(self, sx, sy, return_int=True):
        """Return the map x row for the given screen coordinates."""
        x_off, y_off = self.screen_offset()

        # We're going to use the relative coordinates of the tiles instead of the screen coordinates.
        rx = sx - x_off
        ry = sy - y_off

        # Calculate the x position of map_x tile 0 at ry.
        ox = float(-ry * self.half_tile_width) / float(self.half_tile_height)

        # Now that we have that x origin, we can determine this screen position's x coordinate by dividing by the
        # tile width. Fantastic.
        if return_int:
            # Because of the way Python handles division, we need to apply a little nudge right here.
            if rx - ox < 0:
                ox += self.tile_width
            return int(math.floor((rx - ox) / self.tile_width))
        else:
            return (rx - ox) / self.tile_width

    def map_y(self, sx, sy, return_int=True):
        """Return the map y row for the given screen coordinates."""
        x_off, y_off = self.screen_offset()

        # We're going to use the relative coordinates of the tiles instead of the screen coordinates.
        rx = sx - x_off
        ry = sy - y_off

        oy = float(rx * self.half_tile_height) / float(self.half_tile_width)

        # Now that we have that x origin, we can determine this screen position's x coordinate by dividing by the
        # tile width. Fantastic.
        if return_int:
            # Because of the way Python handles division, we need to apply a little nudge right here.
            if ry - oy < 0:
                oy += self.tile_height
            return int(math.floor((ry - oy) / self.tile_height))
        else:
            return (ry - oy) / self.tile_height

    @property
    def mouse_tile(self):
        if self.cursor:
            return self.cursor.x, self.cursor.y
        else:
            return self._mouse_tile

    def on_paint(self, ev):
        # manage the wallpaper blit
        if (not self.block_wallpaper) and self.isometric_map.wallpaper:
            self.fill_wallpaper()
        else:
            self.screen.fill(self.SOLID_COLOR)

        # -------------------------------------------------------------- OPTIM#2
        need_to_redraw = self.force_redraw_flag
        need_to_redraw = need_to_redraw or (self._focused_object.x != self._focused_object_x0) or \
                         (self._focused_object.y != self._focused_object_y0)
        if need_to_redraw:
            self.focus(self._focused_object.x, self._focused_object.y)
            # TODO can one find a way to optimize without the abusive flag/ that dirty branching?
            if '__BRYTHON__' not in globals():
                self.gfx_data_buffer.fill(self.UPINK)
            else:
                # a hack method, works only with pygame_emu.Surface kengi>v22-10a, thats why i use hasattr(...) here
                if hasattr(self.gfx_data_buffer, 'wreset'):
                    self.gfx_data_buffer.wreset()

            self.impacte_surf(self.gfx_data_buffer)
            self._focused_object_x0 = self._focused_object.x
            self._focused_object_y0 = self._focused_object.y
            self.force_redraw_flag = False
        # -------------------------------------------------------------- OPTIM#2 over.

        if self.MEGAOPTIM:  # floor drawing, the fast way
            a, b = self.screen_offset()
            self.floor_rect.topleft = self.manoffset[0] - a, self.manoffset[1] - b
            self.screen.blit(self.scrollable_floor, (0, 0), area=self.floor_rect)

        self.screen.blit(self.gfx_data_buffer, (0, 0))  # buildings & the player!

        if self.cursor and self.cursor.visible:
            # if self.cursor.layer_name == layer.name:
            # if (x == self.cursor.x) and (y == self.cursor.y):
            # old way:
            # self.cursor.render(self)
            # new way:
            cu = self.cursor
            sx, sy = self.screen_coords(*cu.get_pos())
            mylayer = self.isometric_map.get_layer_by_name(cu.layer_name)
            mydest = cu.surf.get_rect(midtop=(sx + mylayer.offsetx, sy + mylayer.offsety - 2))
            self.screen.blit(cu.surf, mydest)

        # - the new chunk of code that draws objects! {NEW CHUNK OBJ DRAW}
        for mapobj, screen_pos in self.info_draw_mapobj.items():
            if (not mapobj.visible) or isinstance(mapobj, self.pc_cls):
                pass
            else:
                mapobj(self.screen, screen_pos[0], screen_pos[1], self.isometric_map)

        # if an extra anim for the avatar, we use it on the top of everything else
        if (not self._show_avatar) and (self.extra_anim is not None):
            self.av_phase += 1
            if self.av_phase >= self.av_phase_thresh:
                self.av_phase = 0
                if self.av_frame < self.extra_anim.card - 1:
                    self.av_frame += 1
                if self.av_frame > 5:
                    self.anim_av_offset[0] += 1.75
                    self.anim_av_offset[1] -= 0.24
                    self.cutav_cpt += 1
                    base = self.extra_anim[self.av_frame]
                    kappa = self.cutav_cpt
                    self.cutav = base.subsurface((0, kappa, base.get_width() - kappa, base.get_height() - kappa))
            # display avatar alt anim/sprite
            self.screen.blit(  # DIRTY but i dunno how to do better:
                self.extra_anim[self.av_frame] if (self.cutav is None) else self.cutav,
                (160 + int(self.anim_av_offset[0]), 118 + int(self.anim_av_offset[1]))
            )

    def on_mousemotion(self, ev):
        mouse_x, mouse_y = core.proj_to_vscreen(ev.pos)

        self.lastmousepos = (mouse_x, mouse_y)
        self._mouse_tile = (self.map_x(mouse_x, mouse_y, False), self.map_y(mouse_x, mouse_y, False))

        if self.cursor:
            self.cursor.set_position(self.isometric_map, *self._mouse_tile)

    def screen_coords(self, x, y, extra_x_offset=0, extra_y_offset=0):
        x_off, y_off = self.screen_offset()
        return relative_x(x, y) + x_off + extra_x_offset, relative_y(x, y) + y_off + extra_y_offset

    def screen_offset(self):
        return self.mid[0] - relative_x(self._focus_x, self._focus_y), \
               self.mid[1] - relative_y(self._focus_x, self._focus_y)

    def set_focused_object(self, fo):
        if fo:
            self._focused_object = fo
            self.focus(fo.x, fo.y)
        else:
            self._focused_object = None

    def switch_map(self, isometric_map):
        self.force_redraw_flag = True  # obvious that we will have to redraw all!

        # ---------- MEGAOPTIM
        if self.MEGAOPTIM:
            if isometric_map.mapname == 'city':
                self.scrollable_floor = self.FLOORS[0]
                self.manoffset = self.FLOOR_MAN_OFFSET[0]
            elif isometric_map.mapname == 'casino':
                self.scrollable_floor = self.FLOORS[1]
                self.manoffset = self.FLOOR_MAN_OFFSET[1]

        self.isometric_map = isometric_map
        self.tile_width = isometric_map.tile_width
        self.tile_height = isometric_map.tile_height

        self.half_tile_width = isometric_map.tile_width // 2
        self.half_tile_height = isometric_map.tile_height // 2
        rel_set_info(
            self.half_tile_width, self.half_tile_height
        )

        if self._focused_object:
            fo = self._focused_object
            self.focus(fo.x, fo.y)
        else:
            self._focus_x = 0
            self._focus_y = 0
