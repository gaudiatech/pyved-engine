"""
Barebones isometric_map handling for an isometric RPG. For game-specific data,
either subclass the Scene or just declare whatever extra bits are needed.
"""

import collections
import json
import os
import struct
from base64 import b64decode
from xml.etree import ElementTree
from zlib import decompress

import katagames_engine as kengi


SCROLL_STEP = 8
FLIPPED_HORIZONTALLY_FLAG = 0x80000000
FLIPPED_VERTICALLY_FLAG = 0x40000000
FLIPPED_DIAGONALLY_FLAG = 0x20000000
ROTATED_HEXAGONAL_120_FLAG = 0x10000000
NOT_ALL_FLAGS = 0x0FFFFFFF

#
pygame = kengi.pygame
Tilesets = kengi.tmx.data.Tilesets


class IsometricTile():
    def __init__(self, id, tile_surface, hflip, vflip):
        self.id = id
        self.tile_surface = tile_surface
        if hflip:
            self.hflip_surface = pygame.transform.flip(tile_surface, True, False).convert_alpha()
            self.hflip_surface.set_colorkey(tile_surface.get_colorkey(), tile_surface.get_flags())
        else:
            self.hflip_surface = None

        if vflip:
            self.vflip_surface = pygame.transform.flip(tile_surface, False, True).convert_alpha()
            self.vflip_surface.set_colorkey(tile_surface.get_colorkey(), tile_surface.get_flags())
        else:
            self.vflip_surface = None

        if hflip and vflip:
            self.hvflip_surface = pygame.transform.flip(tile_surface, True, True).convert_alpha()
            self.hvflip_surface.set_colorkey(tile_surface.get_colorkey(), tile_surface.get_flags())
        else:
            self.hvflip_surface = None

    def __call__(self, dest_surface, x, y, hflip=False, vflip=False):
        """Draw this tile on the dest_surface at the provided x,y coordinates."""
        if hflip and vflip:
            surf = self.hvflip_surface
        elif hflip:
            surf = self.hflip_surface
        elif vflip:
            surf = self.vflip_surface
        else:
            surf = self.tile_surface
        mydest = surf.get_rect(midbottom=(x, y))
        dest_surface.blit(surf, mydest)

    def __repr__(self):
        return '<Tile {}>'.format(self.id)


class IsometricTileset:
    """
    Based on the Tileset class from katagames_engine/_sm_shelf/tmx/data.py, but modified for the needs of isometric
    maps. Or at least the needs of this particular isometric map.
    """

    def __init__(self, name, tile_width, tile_height, firstgid):
        self.name = name
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.firstgid = firstgid

        self.hflip = False
        self.vflip = False

        self.tiles = []
        self.properties = {}

    def get_tile(self, gid):
        return self.tiles[gid - self.firstgid]

    def _add_image(self, folders, source, num_tiles):
        # TODO: Make this bit compatible with Kenji.
        mysurf = pygame.image.load(os.path.join(os.pathsep.join(folders), source)).convert_alpha()
        mysurf.set_colorkey((255, 0, 255))
        myrect = pygame.Rect(0, 0, self.tile_width, self.tile_height)
        frames_per_row = mysurf.get_width() // self.tile_width

        for frame in range(num_tiles):
            myrect.x = (frame % frames_per_row) * self.tile_width
            myrect.y = (frame // frames_per_row) * self.tile_height
            self.tiles.append(IsometricTile(frame + 1, mysurf.subsurface(myrect), self.hflip, self.vflip))

    @classmethod
    def fromxml(cls, folders, tag, firstgid=None):
        print('fromxml (isometrically)')
        if 'source' in tag.attrib:
            # Instead of a tileset proper, we have been handed an external tileset tag from inside a map file.
            # Load the external tileset and continue on as if nothing had happened.
            firstgid = int(tag.attrib['firstgid'])
            srcc = tag.attrib['source']

            # TODO: Another direct disk access here.
            if srcc.endswith(("tsx", "xml")):
                with open(os.path.join(os.pathsep.join(folders), srcc)) as f:
                    print('opened ', srcc)
                    tag = ElementTree.fromstring(f.read())
            elif srcc.endswith(("tsj", "json")):
                with open(os.path.join(os.pathsep.join(folders), srcc)) as f:
                    jdict = json.load(f)
                return cls.fromjson(folders, jdict, firstgid)

        name = tag.attrib['name']
        if firstgid is None:
            firstgid = int(tag.attrib['firstgid'])
        tile_width = int(tag.attrib['tilewidth'])
        tile_height = int(tag.attrib['tileheight'])
        num_tiles = int(tag.attrib['tilecount'])

        tileset = cls(name, tile_width, tile_height, firstgid)

        # TODO: The transformations must be registered before any of the tiles. Is there a better way to do this
        # than iterating through the list twice? I know this is a minor thing but it bothers me.
        for c in tag:  # .getchildren():
            if c.tag == "transformations":
                tileset.vflip = int(c.attrib.get("vflip", 0)) == 1
                tileset.hflip = int(c.attrib.get("hflip", 0)) == 1
                print("Flip values: v={} h={}".format(tileset.vflip, tileset.hflip))

        for c in tag:  # .getchildren():
            # TODO: The tileset can only contain an "image" tag or multiple "tile" tags; it can't combine the two.
            # This should be enforced. For now, I'm just gonna support spritesheet tiles.
            if c.tag == "image":
                # create a tileset
                arg_sheet = c.attrib['source']
                tileset._add_image(folders, arg_sheet, num_tiles)

        return tileset

    @classmethod
    def fromjson(cls, folders, jdict, firstgid=None):
        print('fromjson (isometrically)')
        if 'source' in jdict:
            firstgid = int(jdict['firstgid'])
            srcc = jdict['source']

            # TODO: Another direct disk access here.
            if srcc.endswith(("tsx", "xml")):
                with open(os.path.join(os.pathsep.join(folders), srcc)) as f:
                    print('opened ', srcc)
                    tag = ElementTree.fromstring(f.read())
                    return cls.fromxml(tag, firstgid)
            elif srcc.endswith(("tsj", "json")):
                with open(os.path.join(os.pathsep.join(folders), srcc)) as f:
                    jdict = json.load(f)

        name = jdict['name']
        if firstgid is None:
            firstgid = int(jdict.get('firstgid', 1))
        tile_width = int(jdict['tilewidth'])
        tile_height = int(jdict['tileheight'])
        num_tiles = int(jdict['tilecount'])

        tileset = cls(name, tile_width, tile_height, firstgid)

        if "transformations" in jdict:
            c = jdict["transformations"]
            tileset.vflip = int(c.get("vflip", 0)) == 1
            tileset.hflip = int(c.get("hflip", 0)) == 1

        # TODO: The tileset can only contain an "image" tag or multiple "tile" tags; it can't combine the two.
        # This should be enforced. For now, I'm just gonna support spritesheet tiles.

        # create a tileset
        arg_sheet = jdict['image']
        tileset._add_image(folders, arg_sheet, num_tiles)

        return tileset


class IsometricMapObject:
    """A thing that can be placed on the map."""

    def __init__(self, **keywords):
        self.name = ""
        self.type = ""
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.gid = 0
        self.visible = 1
        super().__init__(**keywords)

    def __call__(self, dest_surface, sx, sy, mymap):
        """Draw this object at the requested surface coordinates on the provided surface."""
        if self.gid:
            tile_id = self.gid & NOT_ALL_FLAGS
            if tile_id > 0:
                my_tile = mymap.tilesets[tile_id]
                my_tile(dest_surface, sx, sy, self.gid & FLIPPED_HORIZONTALLY_FLAG,
                        self.gid & FLIPPED_VERTICALLY_FLAG)

    @staticmethod
    def _deweirdify_coordinates(tx, ty, givenlayer):
        # It took ages to figure out the coordinate system that Tiled uses for objects on isometric maps. At first I
        # thought the pixel coordinate origin would be the upper left corner of the map's bounding box. It isn't.
        # In fact, it isn't a normal cartesian coordinate system at all. The pixel x,y values are the cell index
        # multiplied by the cell height. I cannot think of any situation for which this would be a useful way to store
        # pixel coordinates, but there you go.
        #
        # This function takes the Tiled pixel coordinates and changes them to tilemap cell coordinates. Feel free to
        # delete this long rant of a comment. Or leave it as a warning to others. I am just glad to finally understand
        # what's going on.

        mx = tx / float(givenlayer.tile_height) - 1.5
        my = ty / float(givenlayer.tile_height) - 1.5
        return mx, my

    @classmethod
    def fromxml(cls, tag, objectgroup, givenlayer):
        myob = cls()
        myob.name = tag.attrib.get("name")
        myob.type = tag.attrib.get("type")
        # Convert the x,y pixel coordinates to x,y map coordinates.
        x = float(tag.attrib.get("x", 0))
        y = float(tag.attrib.get("y", 0))
        myob.x, myob.y = cls._deweirdify_coordinates(x, y, givenlayer)
        myob.gid = int(tag.attrib.get("gid"))
        myob.visible = int(tag.attrib.get("visible", 1))
        return myob

    @classmethod
    def fromjson(cls, jdict, objectgroup, givenlayer):
        myob = cls()
        myob.name = jdict.get("name")
        myob.type = jdict.get("type")
        # Convert the x,y pixel coordinates to x,y map coordinates.
        x = jdict.get("x", 0)
        y = jdict.get("y", 0)
        myob.x, myob.y = cls._deweirdify_coordinates(x, y, givenlayer)
        myob.gid = jdict.get("gid")
        myob.visible = jdict.get("visible")
        return myob


class IsometricLayer:
    def __init__(self, name, visible, map, offsetx=0, offsety=0):
        self.name = name
        self.visible = visible

        self.tile_width = map.tile_width
        self.tile_height = map.tile_height

        self.width = map.width
        self.height = map.height

        self.offsetx = offsetx
        self.offsety = offsety

        self.properties = {}
        self.cells = list()

    def __repr__(self):
        return '<Layer "%s" at 0x%x>' % (self.name, id(self))

    @classmethod
    def emptylayer(cls, name, givenmap):
        layer = cls(
            name, 0, givenmap, 0, 0
        )

        layer.cells = [0, ] * givenmap.height * givenmap.width

        return layer

    @classmethod
    def fromxml(cls, tag, givenmap):
        layer = cls(
            tag.attrib['name'], int(tag.attrib.get('visible', 1)), givenmap,
            int(tag.attrib.get('offsetx', 0)), int(tag.attrib.get('offsety', 0))
        )

        data = tag.find('data')
        if data is None:
            raise ValueError('layer %s does not contain <data>' % layer.name)

        data = data.text.strip()
        data = data.encode()  # Convert to bytes
        # Decode from base 64 and decompress via zlib
        data = decompress(b64decode(data))

        # I ran a test today and there's a slight speed advantage in leaving the cells as a list. It's not a big
        # advantage, but it's just as easy for now to leave the data as it is.
        #
        # I'm changing to a list from a tuple in case destructible terrain or modifiable terrain (such as doors) are
        # wanted in the future.
        layer.cells = list(struct.unpack('<%di' % (len(data) / 4,), data))
        assert len(layer.cells) == layer.width * layer.height

        return layer

    @classmethod
    def fromjson(cls, jdict, givenmap):
        layer = cls(
            jdict['name'], jdict.get('visible', True), givenmap,
            jdict.get('offsetx', 0), jdict.get('offsety', 0)
        )

        data = jdict.get('data')
        if data is None:
            raise ValueError('layer %s does not contain <data>' % layer.name)

        data = data.strip()
        data = data.encode()  # Convert to bytes
        # Decode from base 64 and decompress via zlib
        data = decompress(b64decode(data))

        # I ran a test today and there's a slight speed advantage in leaving the cells as a list. It's not a big
        # advantage, but it's just as easy for now to leave the data as it is.
        #
        # I'm changing to a list from a tuple in case destructible terrain or modifiable terrain (such as doors) are
        # wanted in the future.
        layer.cells = list(struct.unpack('<%di' % (len(data) / 4,), data))
        assert len(layer.cells) == layer.width * layer.height

        return layer

    def __len__(self):
        return self.height * self.width

    def _pos_to_index(self, x, y):
        return y * self.width + x

    def __getitem__(self, key):
        x, y = key
        i = self._pos_to_index(x, y)
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.cells[i]

    def __setitem__(self, pos, value):
        x, y = pos
        i = self._pos_to_index(x, y)
        if 0 <= x < self.width and 0 <= y < self.height:
            self.cells[i] = value


class ObjectGroup():
    def __init__(self, name, visible, offsetx, offsety):
        self.name = name
        self.visible = visible
        self.offsetx = offsetx
        self.offsety = offsety

        self.contents = list()

    @classmethod
    def fromxml(cls, tag, givenlayer, object_fun=None):
        mygroup = cls(
            tag.attrib['name'], int(tag.attrib.get('visible', 1)),
            int(tag.attrib.get('offsetx', 0)), int(tag.attrib.get('offsety', 0))
        )

        for t in tag:
            if t.tag == "object":
                if object_fun:
                    pass
                    # mygroup.contents.append(IsometricMapObject.fromxml(t))
                elif "gid" in t.attrib:
                    mygroup.contents.append(IsometricMapObject.fromxml(
                        t, mygroup, givenlayer
                    ))

        return mygroup

    @classmethod
    def fromjson(cls, folders, jdict, givenlayer, object_fun=None):
        mygroup = cls(
            jdict.get('name'), jdict.get('visible', True),
            jdict.get('offsetx', 0), jdict.get('offsety', 0)
        )

        if "objects" in jdict:
            for t in jdict["objects"]:
                if object_fun:
                    pass
                    # mygroup.contents.append(IsometricMapObject.fromxml(t))
                elif "gid" in t.attrib:
                    mygroup.contents.append(IsometricMapObject.fromjson(
                        folders, t, mygroup, givenlayer
                    ))

        return mygroup


class IsometricMap():
    def __init__(self):
        self.tile_width = 0
        self.tile_height = 0
        self.width = 0
        self.height = 0
        self.properties = {}
        self.layers = list()
        self.tilesets = Tilesets()
        self.objectgroups = dict()

    @classmethod
    def load_tmx(cls, folders, filename, object_fun=None):
        # object_fun is a function that can parse a dict describing an object.
        # If None, the only objects that can be loaded are terrain objects.
        with open(os.path.join(os.pathsep.join(folders), filename)) as f:
            tminfo_tree = ElementTree.fromstring(f.read())

        # get most general map informations and create a surface
        tilemap = cls()

        tilemap.width = int(tminfo_tree.attrib['width'])
        tilemap.height = int(tminfo_tree.attrib['height'])
        tilemap.tile_width = int(tminfo_tree.attrib['tilewidth'])
        tilemap.tile_height = int(tminfo_tree.attrib['tileheight'])

        for tag in tminfo_tree.findall('tileset'):
            tilemap.tilesets.add(
                IsometricTileset.fromxml(folders, tag)
                # hacks work only if no more than 1 ts
            )

        for tag in tminfo_tree:
            if tag.tag == 'layer':
                layer = IsometricLayer.fromxml(tag, tilemap)
                tilemap.layers.append(layer)
            elif tag.tag == "objectgroup":
                if not tilemap.layers:
                    # If the first layer on the map is an objectgroup, this is gonna be a problem. Without
                    # a frame of reference, we won't be able to know what tile the object is in, and that is going
                    # to be important information. So, we add an empty layer with no offsets to act as this
                    # objectgroup's frame of reference.
                    tilemap.layers.append(IsometricLayer.emptylayer("The Mysterious Empty Layer", tilemap))
                tilemap.objectgroups[tilemap.layers[-1]] = ObjectGroup.fromxml(tag, tilemap.layers[-1], object_fun)

        return tilemap

    @classmethod
    def load_json(cls, folders, filename, object_fun=None):
        # object_fun is a function that can parse a dict describing an object.
        # If None, the only objects that can be loaded are terrain objects.

        with open(os.path.join(folders, filename)) as f:
            jdict = json.load(f)

        # get most general map informations and create a surface
        tilemap = cls()

        tilemap.width = jdict['width']
        tilemap.height = jdict['height']
        tilemap.tile_width = jdict['tilewidth']
        tilemap.tile_height = jdict['tileheight']

        for tag in jdict['tilesets']:
            tilemap.tilesets.add(
                IsometricTileset.fromjson(folders, tag)
            )

        for tag in jdict["layers"]:
            if tag["type"] == 'tilelayer':
                layer = IsometricLayer.fromjson(tag, tilemap)
                tilemap.layers.append(layer)
            elif tag["type"] == "objectgroup":
                if not tilemap.layers:
                    # See above comment for why I'm adding an empty layer. TLDR: the objects need a reference frame.
                    tilemap.layers.append(IsometricLayer.emptylayer("The Mysterious Empty Layer", tilemap))
                tilemap.objectgroups[tilemap.layers[-1]] = ObjectGroup.fromjson(folders, tag, tilemap.layers[-1], object_fun)

        return tilemap

    @classmethod
    def load(cls, folders, filename, object_fun=None):
        if filename.endswith(("tmx", "xml")):
            return cls.load_tmx(folders, filename, object_fun)
        elif filename.endswith(("tmj", "json")):
            return cls.load_json(folders, filename, object_fun)

    def on_the_map(self, x, y):
        # Returns true if (x,y) is on the map, false otherwise
        return (x >= 0) and (x < self.width) and (y >= 0) and (y < self.height)

    def get_layer_by_name(self, layer_name):
        # The Layers type in Kengi supports indexing layers by name, but it doesn't support accessing layers by
        # negative indices. I'm not sure that it supports slicing either. Anyhow, for now, only the map cursor needs
        # to look up layers by name so this function should be good enough for the time being.
        for l in self.layers:
            if l.name == layer_name:
                return l


class IsometricMapViewer(object):
    def __init__(self, isometric_map, screen, postfx=None, cursor=None,
                 left_scroll_key=None, right_scroll_key=None, up_scroll_key=None, down_scroll_key=None):

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

        #self.debug_sprite = image.Image("assets/floor-tile.png")

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

    def __call__(self):
        """Draws this mapview to the provided screen."""
        screen_area = self.screen.get_rect()
        mouse_x, mouse_y = kengi.core.proj_to_vscreen(pygame.mouse.get_pos())

        self.screen.fill('black')
        self.camera_updated_this_frame = False
        if self._focused_object and (self._focused_object_x0 != self._focused_object.x or
                                     self._focused_object_y0 != self._focused_object.y):
            self.focus(self._focused_object.x, self._focused_object.y)
            self._focused_object_x0 = self._focused_object.x
            self._focused_object_y0 = self._focused_object.y
        else:
            self._check_mouse_scroll(screen_area, mouse_x, mouse_y)
        x, y = self.map_x(0, 0) - 2, self.map_y(0, 0) - 1
        x0, y0 = x, y
        keep_going = True
        line_number = 1
        line_cache = list()

        # The visible area describes the region of the map we need to draw. It is bigger than the physical screen
        # because we probably have to draw cells that are not fully on the map.
        visible_area = self.screen.get_rect()
        visible_area.inflate_ip(self.tile_width, self.isometric_map.tile_height)
        visible_area.h += self.isometric_map.tile_height + self.half_tile_height - self.isometric_map.layers[-1].offsety

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
                                my_tile(self.screen, sx, sy + layer.offsety, gid & FLIPPED_HORIZONTALLY_FLAG,
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
                                    ob(self.screen, sx, sy, self.isometric_map)

                    elif line_cache[current_line] is None and layer == self.isometric_map.layers[-1]:
                        keep_going = False

                else:
                    break

                if layer.offsety < current_y_offset:
                    current_line -= 1
                    current_y_offset = layer.offsety

            line_number += 1

        #mx = self.map_x(mouse_x, mouse_y)
        #my = self.map_y(mouse_x, mouse_y)
        #if self.isometric_map.on_the_map(mx, my):
        #    mydest = self.debug_sprite.bitmap.get_rect(midbottom=self.screen_coords(mx, my))
        #    self.debug_sprite.render(mydest, 0)

        self.phase = (self.phase + 1) % 600
        self._mouse_tile = (self.map_x(mouse_x, mouse_y), self.map_y(mouse_x, mouse_y))

        if self.postfx:
            self.postfx()

    def check_event(self, ev):
        # Call this function every time your game loop gets an event.
        if self.cursor:
            self.cursor.update(self, ev)
        mykeys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if self.up_scroll_key and mykeys[self.up_scroll_key]:
            dy = SCROLL_STEP
        elif self.down_scroll_key and mykeys[self.down_scroll_key]:
            dy = -SCROLL_STEP
        if self.left_scroll_key and mykeys[self.left_scroll_key]:
            dx = SCROLL_STEP
        elif self.right_scroll_key and mykeys[self.right_scroll_key]:
            dx = -SCROLL_STEP
        if dx or dy:
            self._update_camera(dx, dy)


class IsometricMapCursor(object):
    # I haven't updated this for the new map system yet... I will do that ASAP, even though the QuarterCursor is
    # the one that will be useful for Niobepolis.
    def __init__(self, x, y, image, frame=0, visible=True):
        self.x = x
        self.y = y
        self.image = image
        self.frame = frame
        self.visible = visible

    def render(self, dest: pygame.Rect):
        if self.visible:
            self.image.render(dest, self.frame)

    def set_position(self, scene, x, y, must_be_visible=True):
        if scene.on_the_map(x, y) and (scene.get_visible(x, y) or not must_be_visible):
            self.x, self.y = x, y

    def update(self, view, ev):
        if ev.type == pygame.MOUSEMOTION:
            self.set_position(view.isometric_map, *view._mouse_tile)
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_KP8:
                self.set_position(view.isometric_map, self.x - 1, self.y - 1)
                view.focus(self.x, self.y)
            elif ev.key == pygame.K_KP9:
                self.set_position(view.isometric_map, self.x, self.y - 1)
                view.focus(self.x, self.y)
            elif ev.key == pygame.K_KP6:
                self.set_position(view.isometric_map, self.x + 1, self.y - 1)
                view.focus(self.x, self.y)
            elif ev.key == pygame.K_KP3:
                self.set_position(view.isometric_map, self.x + 1, self.y)
                view.focus(self.x, self.y)
            elif ev.key == pygame.K_KP2:
                self.set_position(view.isometric_map, self.x + 1, self.y + 1)
                view.focus(self.x, self.y)
            elif ev.key == pygame.K_KP1:
                self.set_position(view.isometric_map, self.x, self.y + 1)
                view.focus(self.x, self.y)
            elif ev.key == pygame.K_KP4:
                self.set_position(view.isometric_map, self.x - 1, self.y + 1)
                view.focus(self.x, self.y)
            elif ev.key == pygame.K_KP7:
                self.set_position(view.isometric_map, self.x - 1, self.y)
                view.focus(self.x, self.y)


class IsometricMapQuarterCursor(object):
    # A cursor that only takes up one quarter of a tile.
    def __init__(self, x, y, surf, layer, visible=True):
        self._doublex = int(x*2)
        self._doubley = int(y*2)
        self.surf = surf
        self.layer_name = layer.name
        self.visible = visible

    def render(self, view):
        if self.visible:
            sx, sy = view.screen_coords(float(self._doublex-1)/2.0, float(self._doubley-1)/2.0)
            mylayer = view.isometric_map.get_layer_by_name(self.layer_name)
            mydest = self.surf.get_rect(midbottom=(sx+mylayer.offsetx, sy+mylayer.offsety-2))
            view.screen.blit(self.surf, mydest)

    def set_position(self, view, x, y):
        self._doublex = int(x*2)
        self._doubley = int(y*2)

    @property
    def x(self):
        return self._doublex//2

    @property
    def y(self):
        return self._doubley//2

    def focus(self, view):
        view.focus(float(self._doublex - 1) / 2.0, float(self._doubley - 1) / 2.0)

    def update(self, view, ev):
        if ev.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = kengi.core.proj_to_vscreen(pygame.mouse.get_pos())
            self.set_position(view, view.map_x(mouse_x, mouse_y, return_int=False),
                              view.map_y(mouse_x, mouse_y, return_int=False))
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_KP8:
                self._doublex -= 1
                self._doubley -= 1
                self.focus(view)
            elif ev.key == pygame.K_KP9:
                self._doubley -= 1
                self.focus(view)
            elif ev.key == pygame.K_KP6:
                self._doublex += 1
                self._doubley -= 1
                self.focus(view)
            elif ev.key == pygame.K_KP3:
                self._doublex += 1
                self.focus(view)
            elif ev.key == pygame.K_KP2:
                self._doublex += 1
                self._doubley += 1
                self.focus(view)
            elif ev.key == pygame.K_KP1:
                self._doubley += 1
                self.focus(view)
            elif ev.key == pygame.K_KP4:
                self._doublex -= 1
                self._doubley += 1
                self.focus(view)
            elif ev.key == pygame.K_KP7:
                self._doublex -= 1
                self.focus(view)
