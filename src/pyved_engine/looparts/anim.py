import json

from .. import _hub
from ..compo import gfx


pygame = _hub.pygame

# - check your .json file to be sure the format is well-specified in the code
# cf it matches what's written below
ENUM_FRAMES_ENTRY = 'seq'
DELAY_ENTRY = 'delay'


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, srcpath):
        super().__init__()
        self.image = None

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
                    gfx.Spritesheet(fullsheet, 1).load_strip(
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
