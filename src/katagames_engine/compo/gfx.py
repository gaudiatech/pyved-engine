import json
from .. import _hub
from collections import defaultdict


class JsonBasedSprSheet:
    def __init__(self, filename_no_ext):
        self.sheet_surf = _hub.pygame.image.load(filename_no_ext+'.png')
        json_def_filepath = filename_no_ext+'.json'

        with open(json_def_filepath, 'r') as json_def_file:
            jsondata = json.load(json_def_file)
            assoc_tmp = dict()
            self.all_names = set()
            for infos in jsondata['frames']:
                gname = infos['filename']
                self.all_names.add(gname)
                assoc_tmp[gname] = self.sheet_surf.subsurface(
                    _hub.pygame.Rect(infos['frame']['x'], infos['frame']['y'], infos['frame']['w'], infos['frame']['h'])
                ).copy()
            self.assoc_name_spr = assoc_tmp

    def __getitem__(self, item):
        return self.assoc_name_spr[item]


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
            self._sheet = homo(self._sheet, (chosen_scale*w, chosen_scale*h))

        print('** SHEET size ** ', self._sheet.get_size())

        # can be init later
        self._per_line_img_quant = 0
        self._size = 0
        self._tilesize = None

        self.colorkey = None

        # goal: speed-up
        self.cache = defaultdict(lambda: None)

    @property
    def card(self):
        return self._size

    @property
    def tilesize(self):
        return self._tilesize

    @tilesize.setter
    def tilesize(self, pair_wh):
        print('** tilesize set **', pair_wh)
        self._tilesize = tw, th = pair_wh
        # compute the nb of img and how many img per line
        self._per_line_img_quant = self._sheet.get_width() // tw
        self._size = self._per_line_img_quant * (self._sheet.get_height() // th)
        self.cache.clear()

    def __getitem__(self, item):
        return self.image_by_rank(item)

    def image_at(self, rectangle):
        y = self._sheet.subsurface(rectangle).copy()
        if self.colorkey:
            y.set_colorkey(self.colorkey)
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
            rect_obj = _hub.pygame.Rect(i*self._tilesize[0], j*self._tilesize[1], tw, th)
            # crop from the sheet save & return the result
            y = self.cache[kval] = self.image_at(rect_obj)
        return y

    # USE WITH CAUTION! This method provides no optimization
    def load_strip(self, rect_img0, image_count, colorkey=None):
        """Loads a strip of images and returns them as a list, rect must cut out the img rank 0"""
        rect = rect_img0
        tw, th = rect[2], rect[3]
        tups = [(rect[0] + x*tw, rect[1], tw, th) for x in range(image_count)]
        return self.images_at(tups, colorkey)
