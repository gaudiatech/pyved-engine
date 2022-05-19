import collections
from ... import _hub
from .isosm_config import SCROLL_STEP, NOT_ALL_FLAGS, FLIPPED_VERTICALLY_FLAG, FLIPPED_HORIZONTALLY_FLAG


pygame = _hub.pygame
EngineEvTypes = _hub.event.EngineEvTypes


class IsometricMapViewer(_hub.event.EventReceiver):
    def __init__(self, isometric_map, screen, postfx=None, cursor=None,
                 left_scroll_key=None, right_scroll_key=None, up_scroll_key=None, down_scroll_key=None):
        super().__init__()

        self.isometric_map = isometric_map
        self.screen = screen
        self.x_off = 600
        self.y_off = -200
        self.phase = 0

        self.tile_width = isometric_map.tile_width
        self.tile_height = isometric_map.tile_height
        self.half_tile_width = isometric_map.tile_width // 2
        self.half_tile_height = isometric_map.tile_height // 2

        # _mouse_tile contains the actual tile the mouse is hovering over. However, in most cases what we really want
        # is the location of the mouse cursor. Time to make a property!
        self._mouse_tile = (-1, -1)

        self.postfx = postfx

        self.cursor = cursor

        self.left_scroll_key = left_scroll_key
        self.right_scroll_key = right_scroll_key
        self.up_scroll_key = up_scroll_key
        self.down_scroll_key = down_scroll_key

        self.camera_updated_this_frame = False

        self._focused_object = None
        self._focused_object_x0 = 0
        self._focused_object_y0 = 0

        self.debug_sprite = pygame.image.load('xassets/half-floor-tile.png')  #image.Image("assets/floor-tile.png")
        self.lastmousepos = None

    def set_focused_object(self, fo):
        if fo:
            self._focused_object = fo
            self._focused_object_x0 = fo.x
            self._focused_object_y0 = fo.y
        else:
            self._focused_object = None

    def switch_map(self, isometric_map):
        self.isometric_map = isometric_map
        self.tile_width = isometric_map.tile_width
        self.tile_height = isometric_map.tile_height
        self.half_tile_width = isometric_map.tile_width // 2
        self.half_tile_height = isometric_map.tile_height // 2
        self._check_origin()

    @property
    def mouse_tile(self):
        if self.cursor:
            return self.cursor.x, self.cursor.y
        else:
            return self._mouse_tile

    def relative_x(self, x, y):
        """Return the relative x position of this tile, ignoring offset."""
        return (x * self.half_tile_width) - (y * self.half_tile_width)

    def relative_y(self, x, y):
        """Return the relative y position of this tile, ignoring offset."""
        return (y * self.half_tile_height) + (x * self.half_tile_height)

    def screen_coords(self, x, y, extra_x_offset=0, extra_y_offset=0):
        return (self.relative_x(x - 1, y - 1) + self.x_off + extra_x_offset,
                self.relative_y(x - 1, y - 1) + self.y_off + extra_y_offset)

    def _default_offsets_case(self, a, b):
        if a is None:
            a = self.x_off
        if b is None:
            b = self.y_off
        return a, b

    @staticmethod
    def static_map_x(rx, ry, tile_width, tile_height, half_tile_width, half_tile_height, return_int=True):
        # Return the map coordinates for the relative_x, relative_y coordinates. All x,y offsets- including both
        # the view offset and the layer offset- should already have been applied. This method is needed for calculating
        # the layer coords of objects imported from Tiled, which have pixel coords.
        #
        # Calculate the x position of map_x tile -1 at ry. There is no tile -1, but this is the origin from which we
        # measure everything.
        ox = float(-ry * half_tile_width) / half_tile_height - tile_width

        # Now that we have that x origin, we can determine this screen position's x coordinate by dividing by the
        # tile width. Fantastic.
        if return_int:
            # Because of the way Python handles division, we need to apply a little nudge right here.
            if rx - ox < 0:
                ox += tile_width
            return int((rx - ox) / tile_width) + 1
        else:
            return (rx - ox) / tile_width + 1

    def map_x(self, sx, sy, xoffset_override=None, yoffset_override=None, return_int=True):
        """Return the map x row for the given screen coordinates."""
        x_off, y_off = self._default_offsets_case(xoffset_override, yoffset_override)

        # I was having a lot of trouble with this function, I think because GearHead coordinates use the top left
        # of a square 64x64px cell and for this viewer the map coordinates refer to the midbottom of an arbitrarily
        # sized image. So I broke out some paper and rederived the equations from scratch.

        # We're going to use the relative coordinates of the tiles instead of the screen coordinates.
        rx = sx - x_off
        ry = sy - y_off

        return self.static_map_x(rx, ry, self.tile_width, self.tile_height, self.half_tile_width, self.half_tile_height,
                                 return_int=return_int)

    @staticmethod
    def static_map_y(rx, ry, tile_width, tile_height, half_tile_width, half_tile_height, return_int=True):
        # Return the map coordinates for the relative_x, relative_y coordinates. All x,y offsets- including both
        # the view offset and the layer offset- should already have been applied. This method is needed for calculating
        # the layer coords of objects imported from Tiled, which have pixel coords.
        #
        # Calculate the x position of map_x tile -1 at ry. There is no tile -1, but this is the origin from which we
        # measure everything.
        oy = float(rx * half_tile_height) / half_tile_width - tile_height

        # Now that we have that x origin, we can determine this screen position's x coordinate by dividing by the
        # tile width. Fantastic.
        if return_int:
            # Because of the way Python handles division, we need to apply a little nudge right here.
            if ry - oy < 0:
                oy += tile_height
            return int((ry - oy) / tile_height) + 1
        else:
            return (ry - oy) / tile_height + 1

    def map_y(self, sx, sy, xoffset_override=None, yoffset_override=None, return_int=True):
        """Return the map y row for the given screen coordinates."""
        x_off, y_off = self._default_offsets_case(xoffset_override, yoffset_override)

        # We're going to use the relative coordinates of the tiles instead of the screen coordinates.
        rx = sx - x_off
        ry = sy - y_off

        return self.static_map_y(rx, ry, self.tile_width, self.tile_height, self.half_tile_width, self.half_tile_height,
                                 return_int=return_int)

    def _check_origin(self):
        """Make sure the offset point is within map boundaries."""
        mx = self.map_x(self.screen.get_width() // 2, self.screen.get_height() // 2)
        my = self.map_y(self.screen.get_width() // 2, self.screen.get_height() // 2)

        if not self.isometric_map.on_the_map(mx, my):
            if mx < 0:
                mx = 0
            elif mx >= self.isometric_map.width:
                mx = self.isometric_map.width - 1
            if my < 0:
                my = 0
            elif my >= self.isometric_map.height:
                my = self.isometric_map.height - 1
            self.focus(mx, my)

    def focus(self, x, y):
        """Move the camera to point at the requested map tile. x,y can be ints or floats."""
        if self.isometric_map.on_the_map(int(x+0.99), int(y+0.99)) and not self.camera_updated_this_frame:
            self.x_off = self.screen.get_width() // 2 - self.relative_x(x, y)
            self.y_off = self.screen.get_height() // 2 - self.relative_y(x, y) + self.tile_height
            self.camera_updated_this_frame = True

    def _get_horizontal_line(self, x0, y0, line_number, visible_area):
        mylist = list()
        x = x0 + line_number // 2
        y = y0 + (line_number + 1) // 2

        if self.relative_y(x, y) + self.y_off > visible_area.bottom:
            return None

        while self.relative_x(x - 1, y - 1) + self.x_off < visible_area.right:
            if self.isometric_map.on_the_map(x, y):
                mylist.append((x, y))
            x += 1
            y -= 1
        return mylist

    def _model_depth(self, model):
        return self.relative_y(model.x, model.y)

    def _update_camera(self, dx, dy):
        # If the mouse and the arrow keys conflict, only one of them should win.
        if self.camera_updated_this_frame:
            return

        nu_x_off = self.x_off + dx
        nu_y_off = self.y_off + dy

        mx = self.map_x(self.screen.get_width() // 2, self.screen.get_height() // 2, nu_x_off, nu_y_off)
        my = self.map_y(self.screen.get_width() // 2, self.screen.get_height() // 2, nu_x_off, nu_y_off)

        if self.isometric_map.on_the_map(mx, my):
            self.x_off = nu_x_off
            self.y_off = nu_y_off
            self.camera_updated_this_frame = True

    def _check_mouse_scroll(self, screen_area, mouse_x, mouse_y):
        # Check for map scrolling, depending on mouse position.
        if mouse_x < 20:
            dx = SCROLL_STEP
        elif mouse_x > (screen_area.right - 20):
            dx = -SCROLL_STEP
        else:
            dx = 0

        if mouse_y < 20:
            dy = SCROLL_STEP
        elif mouse_y > (screen_area.bottom - 20):
            dy = -SCROLL_STEP
        else:
            dy = 0

        if dx or dy:
            self._update_camera(dx, dy)

    def proc_event(self, ev, source=None):
        if ev.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = _hub.core.proj_to_vscreen(ev.pos)
            self.lastmousepos = (mouse_x, mouse_y)
            # this was in the __call__ method, previously
            self._mouse_tile = (self.map_x(mouse_x, mouse_y), self.map_y(mouse_x, mouse_y))

            if self.cursor:
                self.cursor.update(self, ev)

        elif ev.type == EngineEvTypes.PAINT:
            ev.screen.fill('black')
            self.camera_updated_this_frame = False
            if self._focused_object and (self._focused_object_x0 != self._focused_object.x or
                                         self._focused_object_y0 != self._focused_object.y):
                self.focus(self._focused_object.x, self._focused_object.y)
                self._focused_object_x0 = self._focused_object.x
                self._focused_object_y0 = self._focused_object.y
            # hack disable temporarely the scroll via mouse.To enable-> uncomment 2 lines below
            # else:
            #    self._check_mouse_scroll(screen_area, mouse_x, mouse_y)

            x, y = self.map_x(0, 0) - 2, self.map_y(0, 0) - 1
            x0, y0 = x, y
            keep_going = True
            line_number = 1
            line_cache = list()

            # The visible area describes the region of the map we need to draw. It is bigger than the physical screen
            # because we probably have to draw cells that are not fully on the map.
            visible_area = ev.screen.get_rect()
            visible_area.inflate_ip(self.tile_width, self.isometric_map.tile_height)
            visible_area.h += self.isometric_map.tile_height + self.half_tile_height - self.isometric_map.layers[
                -1].offsety

            # Record all of the objectgroup contents for display when their tile comes up.
            objectgroup_contents = dict()
            for k, v in self.isometric_map.objectgroups.items():
                objectgroup_contents[k] = collections.defaultdict(list)
                for ob in v.contents:
                    sx, sy = self.screen_coords(ob.x, ob.y, k.offsetx + v.offsetx, k.offsety + v.offsety)
                    obkey = (self.map_x(sx, sy, return_int=True), self.map_y(sx, sy, return_int=True))
                    objectgroup_contents[k][obkey].append(ob)

            while keep_going:
                # In order to allow smooth sub-tile movement of stuff, we have
                # to draw everything in a particular order.
                nuline = self._get_horizontal_line(x0, y0, line_number, visible_area)
                line_cache.append(nuline)
                current_y_offset = self.isometric_map.layers[0].offsety
                current_line = len(line_cache) - 1

                for layer_num, layer in enumerate(self.isometric_map.layers):
                    if current_line >= 0:
                        if line_cache[current_line]:
                            for x, y in line_cache[current_line]:
                                gid = layer[x, y]
                                tile_id = gid & NOT_ALL_FLAGS
                                if tile_id > 0:
                                    my_tile = self.isometric_map.tilesets[tile_id]
                                    sx, sy = self.screen_coords(x, y)
                                    my_tile(ev.screen, sx, sy + layer.offsety, gid & FLIPPED_HORIZONTALLY_FLAG,
                                            gid & FLIPPED_VERTICALLY_FLAG)
                                if self.cursor and self.cursor.layer_name == layer.name and x == self.cursor.x and y == self.cursor.y:
                                    self.cursor.render(self)

                        if current_line > 1 and layer in objectgroup_contents and line_cache[current_line - 1]:
                            # After drawing the terrain, draw any objects in the previous cell.
                            for x, y in line_cache[current_line - 1]:

                                if (x, y) in objectgroup_contents[layer]:
                                    objectgroup_contents[layer][(x, y)].sort(key=self._model_depth)
                                    for ob in objectgroup_contents[layer][(x, y)]:
                                        sx, sy = self.screen_coords(
                                            ob.x, ob.y,
                                            layer.offsetx + self.isometric_map.objectgroups[layer].offsetx,
                                            layer.offsety + self.isometric_map.objectgroups[layer].offsety
                                        )
                                        ob(ev.screen, sx, sy, self.isometric_map)

                        elif line_cache[current_line] is None and layer == self.isometric_map.layers[-1]:
                            keep_going = False

                    else:
                        break

                    if layer.offsety < current_y_offset:
                        current_line -= 1
                        current_y_offset = layer.offsety

                line_number += 1

            # draw cursor org size
            #if self.lastmousepos:
                # mx = self.map_x(self.lastmousepos[0], self.lastmousepos[1])
                # my = self.map_y(self.lastmousepos[0], self.lastmousepos[1])
                # if self.isometric_map.on_the_map(mx, my):
                   ## mydest = self.debug_sprite.bitmap.get_rect(midbottom=self.screen_coords(mx, my))
                   ## mydest = self.debug_sprite.get_rect(midbottom=self.screen_coords(mx, my))
                   # ev.screen.blit(self.debug_sprite, self.screen_coords(mx, my)) # self.debug_sprite.render(mydest, 0)
            # Call this function every time your game loop gets an event.
            if self.cursor:
                self.cursor.update(self, pygame.event.Event(pygame.USEREVENT))

            self.phase = (self.phase + 1) % 600

            if self.postfx:
                self.postfx()

    def scroll_to(self, directioncode):
        """
        :param directioncode: 0 - 3 such as 0 north, 1 east, 2 south, 3 west
        """
        dx = dy = 0
        if 0 == directioncode:
            dy = SCROLL_STEP
        elif 2 == directioncode:
            dy = -SCROLL_STEP
        elif 3 == directioncode:
            dx = SCROLL_STEP
        elif 1 == directioncode:
            dx = -SCROLL_STEP
        else:
            raise ValueError('invalid directioncode: ', directioncode)
        self._update_camera(dx, dy)
