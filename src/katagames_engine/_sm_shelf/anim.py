import json
from .. import _hub as inj


pygame = inj.pygame


class Spritesheet:
    """
    This class handles sprite sheets,
    source-code inspired by: www.scriptefun.com/transcript-2-using
    sprite-sheets-and-drawing-the-background
    Note: When calling images_at the rect is the format:
    (x, y, x + offset, y + offset)
    """

    def __init__(self, ressource_pygame_ratio11, scale=1):
        self.sheet = ressource_pygame_ratio11  # .convert()
        if scale != 1:
            self.sheet = pygame.transform.scale(
                self.sheet, (self.sheet.get_width() * scale, self.sheet.get_height() * scale)
            )

        # can be init later
        self.tilesize = None
        self.img_count_per_line = 0
        self.total_img_count = 0
        self.colorkey = None

    def set_tilesize(self, v):
        self.tilesize = v
        # also need to compute the nb of img and how many img per line
        self.img_count_per_line = self.sheet.get_width() // v[0]
        tmp = self.img_count_per_line
        tmp *= self.sheet.get_height() // v[1]
        self.total_img_count *= tmp

    def image_by_rank(self, kval):
        if self.tilesize is None:
            raise ValueError('calling image_by_rank but the tilesize hasnt been initialized!')
        else:
            # we need to map kval to a rect
            i, j = kval % self.img_count_per_line, int(kval / self.img_count_per_line)
            tw, th = self.tilesize
            r = pygame.Rect(i*tw, j*th, tw, th)
            return self.image_at(r)

    def image_at(self, rectangle, colorkey=None):
        """
        Loads a specific image from a specific rectangle
        :param rectangle: a given (x,y, x+offset,y+offset)
        :param colorkey:  for handling transparency (color identified by colorkey is not drawn)
        :return: pygame surface
        """
        if colorkey is None:
            if self.colorkey is not None:
                colorkey = self.colorkey

        rect = pygame.Rect(rectangle)
        # convert() converts to the same pixel format as the display Surface
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)  # blits sheet's rect to (0,0) in image
        if colorkey is not None:
            image.set_colorkey(colorkey)

        return image

    def images_at(self, rects, colorkey):
        """
        Loads a bunch of images at once
        :param rects: a list of coordinates
        :param colorkey:
        :return: several images as a list
        """
        return [self.image_at(rect, colorkey) for rect in rects]

    def load_strip(self, rect, image_count, colorkey=None):
        """Loads a strip of images and returns them as a list, rect must cut out the 1st img"""
        tups = [(rect[0] + rect[2] * x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)


ENUM_FRAMES_ENTRY = 'seq'
DELAY_ENTRY = 'delay'


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, srcpath):
        super().__init__()
        self.img_source = srcpath + '.png'
        self.infospath = srcpath + '.json'

        self._twidth, self._theight = None, None
        self._ck_desc = None
        self.total_nb_img = 0

        self._data = None
        self._animations = dict()  # the default anim always has the name "idle"

        self.rect = None

        # for one given animation
        self._curr_anim_name = None
        self._curr_img_list = None
        self._curr_nb_frames = 0
        self.k = 0
        self.delay_per_frame = 100 / 1000  # 100ms by default
        self.stack_time = 0

    def __getattr__(self, name):
        print('warning! no preloading has been done on AnimatedSprite inst. ({})'.format(self.img_source))
        if name == 'image':
            self.preload()
            return self.image

    def preload(self):
        fullsheet = pygame.image.load(self.img_source)
        fs_width, fs_height = fullsheet.get_size()

        with open(self.infospath, 'r') as fptr:
            infos_obj = json.load(fptr)
            self._twidth, self._theight = infos_obj['tilesize']
            self._ck_desc = infos_obj['colorkey']
            padding = int(infos_obj['padding'])

            self.total_nb_img = 12  # TODO is this a bug ?

            # -- algorithm:
            # 1) find how many lines & colums
            # 2) put everything in a temp list
            # 3) filter out empty frames (thx to the given padding value)
            # step one
            ncolumns, nlines = fs_width // self._twidth, fs_height // self._theight
            # step two
            tmp = list()
            colork = pygame.color.Color(self._ck_desc)
            for lrank in range(nlines):
                tmp.extend(
                    Spritesheet(fullsheet, 1).load_strip(
                        (0, lrank * self._theight, self._twidth, self._theight), ncolumns, colork
                    )
                )
            # step three
            if padding > 0:
                self._data = tmp[:-padding]
            else:
                self._data = tmp
            # done --

            self.total_nb_img = len(self._data)
            print('total_nb_img -- ', self.total_nb_img)
            self._load_anims(infos_obj['animations'])
            self.play('idle')

    def _ensure_list(self, obj):
        if isinstance(obj, str):
            tmp = obj.split('-')
            if len(tmp[1]) == 0:
                a = int(tmp[0])
                b = self.total_nb_img-1
            else:
                a = int(tmp[0])
                b = int(tmp[1])

            return list(range(a, b + 1))
        else:
            return obj


    def _load_anims(self, obj):
        """
        being given a JSON-like structure, example:
        "animations":{
            "idle":{"set":"0-5","delay":100},
            "attack":{"set":[6,7,8,9,10,11],"delay":250}
        }
        this method returns a dict name <> pair a,b
        where a is the list of images,
        b is the interframe delay
        """
        self._animations.clear()

        for k, v in obj.items():
            tmp = list()
            enum_frames = self._ensure_list(v[ENUM_FRAMES_ENTRY])
            for idx in enum_frames:

                if idx >= self.total_nb_img:
                    err_m = 'in animation "{}" given range is {} but, no corresp. data in the SpriteSheet!'.format(
                        k, v[ENUM_FRAMES_ENTRY]
                    )
                    raise ValueError(err_m)
                tmp.append(self._data[idx])
            print('anim {} , img count -- {}'.format(k, len(tmp)))
            self._animations[k] = (tmp, v[DELAY_ENTRY] / 1000)  # defined as millisec

    def play(self, anim_name):
        self._curr_anim_name = anim_name
        self._curr_img_list, self.delay_per_frame = self._animations[anim_name]
        self._curr_nb_frames = len(self._curr_img_list)

        self.image = self._curr_img_list[0]
        if self.rect is None:
            self.rect = self.image.get_rect()

        self.k = 0
        self.stack_time = 0

    def draw(self, screenref):
        # this will bug bc of pygame.transform.scale not properly implemented in pygame_emu (v. 007+)
        screenref.blit(self.image, self.rect.topleft)
        # pygame.draw.rect(screenref, 'red', (self.rect.topleft, (89, 89)))

    def update(self, dt):
        self.stack_time += dt

        if self.stack_time > self.delay_per_frame:
            self.stack_time -= self.delay_per_frame
            self.k += 1
            if self.k >= self._curr_nb_frames:
                self.play('idle')
            self.image = self._curr_img_list[self.k]
