from collections import defaultdict

from . import _hub


class Spritesheet:
    """
    handles sprite sheets in an optimized way!
    REMARK: When calling images_at the rect is the format: (x, y, x + offset, y + offset)
    """

    def __init__(self, resource_info, chosen_scale=1):
        """
        :param resource_info: either pygame.Surface or filepath
        :param chosen_scale:
        """
        if isinstance(resource_info, _hub.pygame.Surface):
            self._sheet = resource_info
        else:
            self._sheet = _hub.pygame.image.load(resource_info).convert()

        if float(chosen_scale) != 1.0:
            homo = _hub.pygame.transform.scale
            w, h = self._sheet.get_size()
            self._sheet = homo(self._sheet, (chosen_scale * w, chosen_scale * h))

        # can be init later
        self._per_line_img_quant = 0
        self._card = 0
        self._tilesize = None

        self._colorkey = None

        # goal: speed-up
        self.cache = defaultdict(lambda: None)
        self._spacing = 0

    @property
    def colorkey(self):
        return self._colorkey

    @colorkey.setter
    def colorkey(self, v):
        self._colorkey = v
        self._cache_update()

    @property
    def card(self):
        return self._card

    @property
    def tilesize(self):
        return self._tilesize

    def set_infos(self, pair_wh, count_tiles=None, nb_columns=None, spacing=0):
        self._tilesize = pair_wh[0], pair_wh[1]

        if count_tiles is not None and nb_columns is not None:
            self._per_line_img_quant = nb_columns
            self._card = count_tiles
        else:
            sz = self._sheet.get_size()
            self._per_line_img_quant = sz[0] // self._tilesize[0]
            self._card = (sz[1] // self._tilesize[1]) * self._per_line_img_quant

        self._spacing = spacing
        # - debug
        # print(
        #     f'infos dans Spritesheet saisies depuis dehors:\n___tilesize {self._tilesize}\n'
        #     + '___count_img {count_tiles}\n___nbcol {nb_columns}\n___spacing {spacing}'
        # )
        self._cache_update()

    def _cache_update(self):
        # re - populate the whole cache!
        self.cache.clear()
        pg = _hub.pygame

        if self._tilesize is None:
            return
        tile_w, tile_h = self._tilesize
        ident = 0
        nb_lines = self._card // self._per_line_img_quant
        for curr_line in range(1, nb_lines + 1):
            for column in range(1, self._per_line_img_quant + 1):
                adhocx = -tile_w + column * tile_w + (column - 1) * self._spacing
                adhocy = -tile_h + curr_line * tile_h + (curr_line - 1) * self._spacing
                decoupe = pg.Rect(adhocx, adhocy, tile_w, tile_h)
                y = self._sheet.subsurface(decoupe)
                if self._colorkey is not None:
                    y.set_colorkey(self._colorkey)
                self.cache[ident] = y
                ident += 1

    @property
    def spacing(self):
        return self._spacing

    def __getitem__(self, item):
        return self.image_by_rank(item)

    def image_at(self, rectangle):
        y = self._sheet.subsurface(rectangle).copy()
        if self._colorkey:
            y.set_colorkey(self._colorkey)
        return y

    # USE WITH CAUTION! This method provides no optimization
    def images_at(self, rects, colorkey):
        """
        Loads a bunch of images at once
        :param rects: a list of coordinates
        :param colorkey:
        :return: several images as a list
        """
        res = [self.image_at(rect) for rect in rects]
        for e in res:
            e.set_colorkey(colorkey)
        return res

    def image_by_rank(self, kval):
        if self._tilesize is None:
            raise ValueError('Spritesheet.image_by_rank call but tilesize hasnt been set!')
        y = self.cache[kval]
        if y is None:
            tw, th = self._tilesize
            # map kval -> to a rect
            i, j = kval % self._per_line_img_quant, int(kval / self._per_line_img_quant)
            rect_obj = _hub.pygame.Rect(i * tw, j * th, tw, th)
            # crop from the sheet save & return the result
            y = self.cache[kval] = self.image_at(rect_obj)
        return y

    # USE WITH CAUTION! This method provides no optimization
    def load_strip(self, rect_img0, image_count, colorkey=None):
        """Loads a strip of images and returns them as a list, rect must cut out the img rank 0"""
        rect = rect_img0
        tw, th = rect[2], rect[3]
        tups = [(rect[0] + x * tw, rect[1], tw, th) for x in range(image_count)]
        return self.images_at(tups, colorkey)

