""" Barebones isometric_map handling for an isometric RPG. For game-specific data,
    either subclass the Scene or just declare whatever extra bits are needed.
"""
from ... import _hub
pygame = _hub.pygame
Tilesets = _hub.tmx.data.Tilesets

import json

from zlib import decompress
from base64 import b64decode

from xml.etree import ElementTree

import struct
import os
import math


SCROLL_STEP = 8
FLIPPED_HORIZONTALLY_FLAG = 0x80000000
FLIPPED_VERTICALLY_FLAG = 0x40000000
FLIPPED_DIAGONALLY_FLAG = 0x20000000
ROTATED_HEXAGONAL_120_FLAG = 0x10000000
NOT_ALL_FLAGS = 0x0FFFFFFF


class IsometricTile:
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

    def _add_image(self, source, num_tiles):
        # TODO: Make this bit compatible with Kenji.
        mysurf = pygame.image.load(os.path.join("assets", source)).convert_alpha()
        mysurf.set_colorkey((255, 0, 255))
        myrect = pygame.Rect(0, 0, self.tile_width, self.tile_height)
        frames_per_row = mysurf.get_width() // self.tile_width

        for frame in range(num_tiles):
            myrect.x = (frame % frames_per_row) * self.tile_width
            myrect.y = (frame // frames_per_row) * self.tile_height
            self.tiles.append(IsometricTile(frame + 1, mysurf.subsurface(myrect), self.hflip, self.vflip))

    @classmethod
    def fromxml(cls, tag, firstgid=None):
        print('fromxml (isometrically)')
        if 'source' in tag.attrib:
            # Instead of a tileset proper, we have been handed an external tileset tag from inside a map file.
            # Load the external tileset and continue on as if nothing had happened.
            firstgid = int(tag.attrib['firstgid'])
            srcc = tag.attrib['source']

            # TODO: Another direct disk access here.
            if srcc.endswith(("tsx", "xml")):
                with open(os.path.join("assets", srcc)) as f:
                    print('opened ', srcc)
                    tag = ElementTree.fromstring(f.read())
            elif srcc.endswith(("tsj", "json")):
                with open(os.path.join("assets", srcc)) as f:
                    jdict = json.load(f)
                return cls.fromjson(jdict, firstgid)

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
                tileset._add_image(arg_sheet, num_tiles)

        return tileset

    @classmethod
    def fromjson(cls, jdict, firstgid=None):
        print('fromjson (isometrically)')
        if 'source' in jdict:
            firstgid = int(jdict['firstgid'])
            srcc = jdict['source']

            # TODO: Another direct disk access here.
            if srcc.endswith(("tsx", "xml")):
                with open(os.path.join("assets", srcc)) as f:
                    print('opened ', srcc)
                    tag = ElementTree.fromstring(f.read())
                    return cls.fromxml(tag, firstgid)
            elif srcc.endswith(("tsj", "json")):
                with open(os.path.join("assets", srcc)) as f:
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
        tileset._add_image(arg_sheet, num_tiles)

        return tileset


class IsometricMapObject():
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
        y = y % self.height
        x = x % self.width
        return y * self.width + x

    def __getitem__(self, key):
        x, y = key
        i = self._pos_to_index(x, y)
        # if 0 <= x < self.width and 0 <= y < self.height:
        return self.cells[i]

    def __setitem__(self, pos, value):
        x, y = pos
        i = self._pos_to_index(x, y)
        # if 0 <= x < self.width and 0 <= y < self.height:
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
    def fromjson(cls, jdict, givenlayer, object_fun=None):
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
                        t, mygroup, givenlayer
                    ))

        return mygroup


class IsometricMap():
    def __init__(self):
        self.tile_width = 0
        self.tile_height = 0
        self.width = 0
        self.height = 0
        self.layers = list()
        self.tilesets = Tilesets()
        self.objectgroups = dict()

        self.wrap_x = False
        self.wrap_y = False

        self.floor_layer = None
        self.wall_layer = None

        self.wallpaper = None

    def seek_floor_and_wall(self):
        for n, layer in enumerate(self.layers):
            if layer.name == "Floor Layer":
                self.floor_layer = n
            elif layer.name == "Wall Layer":
                self.wall_layer = n

    @classmethod
    def load_tmx(cls, filename, object_fun=None):
        # object_fun is a function that can parse a dict describing an object.
        # If None, the only objects that can be loaded are terrain objects.
        with open(filename) as f:
            tminfo_tree = ElementTree.fromstring(f.read())

        # get most general map informations and create a surface
        tilemap = cls()

        tilemap.width = int(tminfo_tree.attrib['width'])
        tilemap.height = int(tminfo_tree.attrib['height'])
        tilemap.tile_width = int(tminfo_tree.attrib['tilewidth'])
        tilemap.tile_height = int(tminfo_tree.attrib['tileheight'])

        for tag in tminfo_tree.findall('tileset'):
            tilemap.tilesets.add(
                IsometricTileset.fromxml(tag)
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
            elif tag.tag == "properties":
                for ptag in tag.findall("property"):
                    if ptag.get("name") == "wrap_x":
                        tilemap.wrap_x = ptag.get("value") == "true"
                    elif ptag.get("name") == "wrap_y":
                        tilemap.wrap_y = ptag.get("value") == "true"
                    elif ptag.get("name") == "wallpaper":
                        tilemap.wallpaper = pygame.image.load(os.path.join("assets",ptag.get("value"))).convert_alpha()


        return tilemap

    @classmethod
    def load_json(cls, filename, object_fun=None):
        # object_fun is a function that can parse a dict describing an object.
        # If None, the only objects that can be loaded are terrain objects.

        with open(filename) as f:
            jdict = json.load(f)

        # get most general map informations and create a surface
        tilemap = cls()

        tilemap.width = jdict['width']
        tilemap.height = jdict['height']
        tilemap.tile_width = jdict['tilewidth']
        tilemap.tile_height = jdict['tileheight']

        if "properties" in jdict:
            for tag in jdict["properties"]:
                if tag["name"] == "wrap_x":
                    tilemap.wrap_x = tag.get("value", False)
                elif tag["name"] == "wrap_y":
                    tilemap.wrap_y = tag.get("value", False)
                elif tag["name"] == "wallpaper":
                    tilemap.wallpaper = pygame.image.load(os.path.join("assets", tag.get("value"))).convert_alpha()


        for tag in jdict['tilesets']:
            tilemap.tilesets.add(
                IsometricTileset.fromjson(tag)
            )

        for tag in jdict["layers"]:
            if tag["type"] == 'tilelayer':
                layer = IsometricLayer.fromjson(tag, tilemap)
                tilemap.layers.append(layer)
            elif tag["type"] == "objectgroup":
                if not tilemap.layers:
                    # See above comment for why I'm adding an empty layer. TLDR: the objects need a reference frame.
                    tilemap.layers.append(IsometricLayer.emptylayer("The Mysterious Empty Layer", tilemap))
                tilemap.objectgroups[tilemap.layers[-1]] = ObjectGroup.fromjson(tag, tilemap.layers[-1], object_fun)

        return tilemap

    @classmethod
    def load(cls, filename, object_fun=None):
        if filename.endswith(("tmx", "xml")):
            mymap = cls.load_tmx(filename, object_fun)
        elif filename.endswith(("tmj", "json")):
            mymap = cls.load_json(filename, object_fun)
        else:
            raise NotImplementedError("No decoder for {}".format(filename))
        mymap.seek_floor_and_wall()
        return mymap

    def on_the_map(self, x, y):
        # Returns true if (x,y) is on the map, false otherwise
        return (self.wrap_x or ((x >= 0) and (x < self.width))) and (self.wrap_y or ((y >= 0) and (y < self.height)))

    def get_layer_by_name(self, layer_name):
        # The Layers type in Kengi supports indexing layers by name, but it
        # doesn't support accessing layers by
        # negative indices. I'm not sure that it supports slicing either. Anyhow, for now, only the map cursor needs
        # to look up layers by name so this function should be good enough for the time being.
        for l in self.layers:
            if l.name == layer_name:
                return l

    def get_object_by_name(self, object_name):
        # Return the first object found with the provided name.
        for obgroup in self.objectgroups.values():
            for ob in obgroup.contents:
                if ob.name == object_name:
                    return ob

    def clamp_pos(self, pos):
        # For infinite scroll maps, clamp the x and/or y values
        nupos = list(pos)
        if self.wrap_x:
            f, i = math.modf(pos[0])
            nupos[0] = int(i) % self.width + f
        else:
            if pos[0] < 0:
                nupos[0] = 0
            elif pos[0] >= self.width:
                nupos[0] = self.width-1
        if self.wrap_y:
            f, i = math.modf(pos[1])
            nupos[1] = int(i) % self.height + f
        else:
            if pos[1] < 0:
                nupos[1] = 0
            elif pos[1] >= self.height:
                nupos[1] = self.height-1
        return tuple(nupos)

    def clamp_pos_int(self, pos):
        # For infinite scroll maps, clamp the x and/or y values
        nupos = [int(math.floor(c)) for c in pos]
        if self.wrap_x:
            f, i = math.modf(pos[0])
            nupos[0] = int(i) % self.width
        else:
            if pos[0] < 0:
                nupos[0] = 0
            elif pos[0] >= self.width:
                nupos[0] = self.width-1
        if self.wrap_y:
            f, i = math.modf(pos[1])
            nupos[1] = int(i) % self.height
        else:
            if pos[1] < 0:
                nupos[1] = 0
            elif pos[1] >= self.height:
                nupos[1] = self.height-1
        return tuple(nupos)

    def tile_is_blocked(self, x, y):
        pos = self.clamp_pos_int((x,y))
        if self.floor_layer is not None and self.layers[self.floor_layer][pos] == 0:
            return True
        if self.wall_layer is not None and self.layers[self.wall_layer][pos] != 0:
            return True
        else:
            return False


class IsometricMapQuarterCursor(object):
    # A cursor that only takes up one quarter of a tile.
    def __init__(self, x, y, surf, layer, visible=True):
        self._doublex = int(x * 2)
        self._doubley = int(y * 2)
        self.surf = surf
        self.layer_name = layer.name
        self.visible = visible

    def render(self, view):
        if self.visible:
            sx, sy = view.screen_coords(*self.get_pos())
            mylayer = view.isometric_map.get_layer_by_name(self.layer_name)
            mydest = self.surf.get_rect(midtop=(sx + mylayer.offsetx, sy + mylayer.offsety - 1))
            view.screen.blit(self.surf, mydest)

    def set_position(self, view, x, y):
        self._doublex = int(x * 2)
        self._doubley = int(y * 2)

    @property
    def x(self):
        return self._doublex // 2

    @property
    def y(self):
        return self._doubley // 2

    def get_pos(self):
        return float(self._doublex) / 2.0, float(self._doubley) / 2.0

    def focus(self, view):
        view.focus(float(self._doublex - 1) / 2.0, float(self._doubley - 1) / 2.0)

    def update(self, view, ev):
        if ev.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = _hub.core.proj_to_vscreen(pygame.mouse.get_pos())
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
