import base64
import io
import json
from abc import abstractmethod
from collections import defaultdict

from . import packed_capello_ft
from .. import _hub


class JsonBasedSprSheet:
    def __init__(self, filename_noext_nopath, pathinfo=None, ck=None, is_webhack=False):
        """
        warning:
        the current source-code looks stupid, but it has written that way in order to
        avoid several bugs that exist in the pyVM component.
        (scaling images, and use .subsurface on these images for cutting sub images)
        As long as the pyVM has not bee toroughly debugged and tested,
        I recommend not modifying the following code, unless you want to take risks
        """

        print('create SpriteSheet based on json:', filename_noext_nopath)

        if is_webhack:
            p = ''
        else:
            p = pathinfo
        open_img= f'{p}{filename_noext_nopath}.png'
        print('open img->', open_img)
        self.sheet_surf = _hub.pygame.image.load(open_img)
        if pathinfo and pathinfo != './':
            p = pathinfo
        json_def_file = open(f'{p}{filename_noext_nopath}.json', 'r')
        jsondata = json.load(json_def_file)

        chosen_scale = "1"
        meta = jsondata.get("meta", "")
        if meta:
            chosen_scale = meta.get("scale", chosen_scale)
            print('[JsonBasedSprSheet] image scale after reading meta field:', chosen_scale)
        else:
            print('[JsonBasedSprSheet] no meta field has been found in the json file')

        try:
            chosen_scale_f = float(chosen_scale)
        except ValueError:
            e_msg = f"[JsonBasedSprSheet:] WARNING! Cannot convert scale '{chosen_scale}' to float, using default val."
            print(e_msg)
            chosen_scale_f = 1.0

        #if chosen_scale_f != 1.0:
        #    w, h = self.sheet_surf.get_size()
        #    self.sheet_surf = _hub.pygame.transform.scale(
        #        self.sheet_surf, (chosen_scale_f * w, chosen_scale_f * h)
        #    )
        if ck:
            self.sheet_surf.set_colorkey(ck)

        assoc_tmp = dict()
        self.all_names = set()
        y = chosen_scale_f
        chosen_scale_f = 1.0
        if isinstance(jsondata['frames'], list):  # we support 2 formats of json desc
            for infos in jsondata['frames']:
                gname = infos['filename']
                self.all_names.add(gname)
                args = (infos['frame']['x'] * chosen_scale_f, infos['frame']['y'] * chosen_scale_f,
                        infos['frame']['w'] * chosen_scale_f, infos['frame']['h'] * chosen_scale_f)
                tempp = self.sheet_surf.subsurface(_hub.pygame.Rect(*args)).copy()
                lw, lh = tempp.get_size()
                assoc_tmp[gname] = _hub.pygame.transform.scale(
                    tempp, (y*lw, y*lh)
                )
        else:
            for sprname, infos in jsondata['frames'].items():
                self.all_names.add(sprname)
                args = (infos['frame']['x'] * chosen_scale_f, infos['frame']['y'] * chosen_scale_f,
                        infos['frame']['w'] * chosen_scale_f, infos['frame']['h'] * chosen_scale_f)
                tempp = self.sheet_surf.subsurface(_hub.pygame.Rect(*args)).copy()
                lw, lh = tempp.get_size()
                assoc_tmp[sprname] = _hub.pygame.transform.scale(
                    tempp, (y*lw, y*lh)
                )

        self.assoc_name_spr = assoc_tmp

    def __getitem__(self, item):
        return self.assoc_name_spr[item]


class BaseCfont:
    UNKNOWN_CAR_RK = 123
    SPAM_CAR = False

    @abstractmethod
    def _init_sheet_attr(self):
        raise NotImplementedError

    def __init__(self):
        self.forcing_transparency = False

        self._sheet = dict()
        self._init_sheet_attr()

        # specific to capello-ft.png and capello-ft.json...
        # it maps ascii codes to the rank font000.png where 000 is the rank
        mappingtable = {
            174: 150,  # circled r car.
            175: 151,
        }
        for e in range(32, 48):
            mappingtable[e] = e - 32
        for e in range(48, 64):
            mappingtable[e] = e - 31
        for e in range(64, 80):
            mappingtable[e] = e - 30
        for e in range(80, 96):
            mappingtable[e] = e - 29
        for e in range(96, 112):
            mappingtable[e] = e - 28
        for e in range(112, 127):
            mappingtable[e] = e - 27
        # upside-down !, cent ¢ , then £ symbol ... etc.
        for e in range(160, 173):
            mappingtable[e] = e - 24

        for e in range(176, 176 + 16):
            mappingtable[e] = e - 23
        for e in range(192, 208):
            mappingtable[e] = e - 22
        # Ð 208 et suivants
        for e in range(208, 224):
            mappingtable[e] = e - 21
        for e in range(224, 240):
            mappingtable[e] = e - 20
        # ð 240 et suivants
        for e in range(240, 256):
            mappingtable[e] = e - 19
        self.car_height = defaultdict(lambda: 7)
        # for my_asciicode in range(*alphabet_span):
        #     self.car_height[chr(my_asciicode)] = 7  # CONST

        # - generic
        self.ascii2img = dict()
        defaultw = self._sheet["tile{:03d}.png".format(self.UNKNOWN_CAR_RK)].get_width()
        self.car_width = defaultdict(lambda: defaultw)

        for my_asciicode in mappingtable.keys():
            ssurf = self._sheet["tile{:03d}.png".format(mappingtable[my_asciicode])]
            self.ascii2img[my_asciicode] = ssurf
            self.car_width[chr(my_asciicode)] = ssurf.get_width()

    @property
    def sheet(self):
        return self._sheet

    def __getitem__(self, itemk):
        ascii_tmp = ord(itemk)
        if self.SPAM_CAR:
            print(itemk, ascii_tmp)
        try:
            return self.ascii2img[ascii_tmp]
        except KeyError:
            return self._sheet['tile{:03d}.png'.format(self.UNKNOWN_CAR_RK)]

    def text_to_surf(self, w, refsurf, start_pos, spacing=0, bgcolor=None):
        # fill background with a solid color, if requested
        if bgcolor:
            curr_pos = list(start_pos)
            h = float('-inf')
            for letter in w:
                curr_pos[0] += self.car_width[letter] + spacing
                if self.car_height[letter] > h:
                    h = self.car_height[letter]
            _hub.pygame.draw.rect(
                refsurf, bgcolor, (start_pos[0], start_pos[1], curr_pos[0] - spacing - start_pos[0], h), 0
            )
        # draw the text
        curr_pos = list(start_pos)
        for letter in w:
            refsurf.blit(self[letter], curr_pos)
            curr_pos[0] += self.car_width[letter] + spacing

    def compute_width(self, w, spacing=0):
        res = 0
        for letter in w:
            res += self.car_width[letter] + spacing
        return res

    # ---------------
    #  lets emulate the pygame API, too
    # ---------------
    def size(self, w):
        fixspacing = 0
        return self.compute_width(w, fixspacing), self.car_height[' ']

    # signature. font.render(l, antialias, color)
    def render(self, textstr, dummy_antialias, dummy_color, spacing=0):
        """
        :param spacing:
        :param textstr:
        :param dummy_antialias: unused, but must be here for API compliance
        :param dummy_color: unused, but must be here for API compliance
        :return: a pygame surface obj!
        """
        aw, ah = self.compute_width(textstr, spacing), self.car_height[' ']
        res = _hub.pygame.Surface((aw, ah))

        opt0 = self.forcing_transparency
        ck_tmp_color = (255, 0, 255)
        if opt0:
            res.fill(ck_tmp_color)
        self.text_to_surf(textstr, res, (0, 0), spacing)
        if opt0:
            res.set_colorkey(ck_tmp_color)

        return res


class JsonBasedCfont(BaseCfont):
    def __init__(self, sourcejson):
        self._known_source = sourcejson
        super().__init__()

    def _init_sheet_attr(self):
        font_source_no_ext = self._known_source
        self._sheet = JsonBasedSprSheet(
            font_source_no_ext, ck=(127, 127, 127)  # font_source could be 'capello-ft' for example
        )


class EmbeddedCfont(BaseCfont):
    def _init_sheet_attr(self):
        # - meth2 : on ouvre du packed data, tt simplement!
        filelike_png = io.BytesIO(base64.b64decode(packed_capello_ft.pngdata))
        filelike_json = io.StringIO(packed_capello_ft.jsondata)
        self._sheet = JsonBasedSprSheet(
            (filelike_png, filelike_json), ck=(127, 127, 127)
        )


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
