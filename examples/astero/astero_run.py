import math
import random

# import katagames_sdk as katasdk
import pyved_engine as kengi
kengi.bootstrap_e()


# Const.
BG_COLOR = (0, 33, 25)  # rgb format
SHIP_COLOR = (119, 255, 0)
BULLET_COLOR = SHIP_COLOR
NB_ROCKS = 4
INSTR = """\
AsteroTempl prototype\n\
**GOAL** Destroy every single asteroid.\n\
**CONTROLS** Use:\n> Left/Right arrows to turn {gamepad> the left stick}\n> Up/Down arrows to control speed {gamepad>Right/Left trigger}\n> Space bar to shoot {gamepad> the A button}\
"""
LAST_LINE = '{gamepad> the START button}'

# Aliases
# kengi = katasdk.kengi
pygame = kengi.pygame

# Misc.
bullets = list()
scr_size = [0, 0]
music_snd = None
view = ctrl = None
Vector2 = kengi.pygame.math.Vector2

MyEvTypes = kengi.game_events_enum((
    'PlayerChanges',  # contains: new_pos, angle
))

PREFIX_ASSET = ''  # 'user_assets/'


def img_load(img_name):
    return pygame.image.load(PREFIX_ASSET + img_name)


def snd_load(path):
    return pygame.mixer.Sound(PREFIX_ASSET+path)


class ShipModel(kengi.Emitter):
    MISSILE_SPEED = 3
    SPEED_CAP = 192
    THRUST_VAL = 0.823
    DELTA_ANGLE = 0.051

    def __init__(self):
        super().__init__()
        self.scr_size = sw, sh = kengi.vscreen.get_screen().get_size()
        self._position = Vector2(sw // 2, sh // 2)
        self._orientation = Vector2(1, 0)
        self._curr_speed = 0.0  # can be negative too

    def reset(self):
        self._position[:] = (scr_size[0] // 2, scr_size[1] // 2)
        self._orientation[:] = (1, 0)
        self._curr_speed = 0.0

    @property
    def pos(self):
        return self._position.x, self._position.y

    @property
    def orientation(self):
        return self._orientation.as_polar()[1]  # returns a value in RAD

    def _clamp_n_broadcast_state(self):
        xcap, ycap = self.scr_size
        if self._position.x < 0:
            self._position.x += xcap
        elif self._position.x >= xcap:
            self._position.x -= xcap
        if self._position.y < 0:
            self._position.y += ycap
        elif self._position.y >= ycap:
            self._position.y -= ycap
        self.pev(MyEvTypes.PlayerChanges, pos=self.pos, orientation=self.orientation)

    def update(self, dt):
        speedvector = Vector2()
        speedvector.from_polar((1, math.degrees(self.orientation)))
        speedvector.x *= self._curr_speed
        speedvector.y *= self._curr_speed
        self._position.x += dt * speedvector.x
        self._position.y += dt * speedvector.y
        self._clamp_n_broadcast_state()

    def ccw_rotate(self):
        _, b = self._orientation.as_polar()
        b += self.DELTA_ANGLE
        self._orientation.from_polar((1, b))
        self._clamp_n_broadcast_state()

    def cw_rotate(self):
        _, b = self._orientation.as_polar()
        b -= self.DELTA_ANGLE
        self._orientation.from_polar((1, b))
        self._clamp_n_broadcast_state()

    def interp_direction(self, given_or):
        self._orientation.from_polar((1, given_or))

    def accelerate(self, v):
        self._curr_speed += self.THRUST_VAL * (1 + v)
        if self._curr_speed > self.SPEED_CAP:
            self._curr_speed = self.SPEED_CAP
        self._clamp_n_broadcast_state()

    def brake(self, v):
        if self._curr_speed > 0:
            self._curr_speed -= (1/v)*0.1*self._curr_speed
            if self._curr_speed < 5:
                self._curr_speed = 0

    def shoot(self):
        global bullets
        sh_pos = Vector2(self.pos)
        b_speed = Vector2()
        b_speed.from_polar((self.MISSILE_SPEED, math.degrees(self.orientation)))
        bullets.append((sh_pos, b_speed))

    def get_position(self):
        return self._position

    def get_scr_pos(self):
        return int(self._position.x), int(self._position.y)

    def set_position(self, new_pos):
        self._position.x, self._position.y = new_pos
        self._commit_new_pos()


class RockSprite(pygame.sprite.Sprite):
    snd = None

    def __init__(self):
        super().__init__()
        if self.__class__.snd:
            pass
        else:
            self.__class__.snd = snd_load('(astero)explosion_002.wav')
            self.__class__.snd.set_volume(0.66)
        self.image = img_load('(astero)rock.png')
        self.image.set_colorkey((0xff, 0, 0xff))
        pos = [random.randint(0, scr_size[0] - 1), random.randint(0, scr_size[1] - 1)]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.vx = random.choice((1, -1)) * random.randint(1, 3)
        self.vy = random.choice((1, -1)) * random.randint(1, 3)
        self.cpt = 1
        self.zombie = False
        self.immunity = 0

    def destroyed(self):
        self.__class__.snd.play(0)

    def update(self):
        if self.immunity:
            self.immunity -= 1
        if self.cpt == 0:
            x, y = self.rect.topleft
            x += self.vx
            y += self.vy
            self.rect.topleft = x, y
            if self.rect.left >= scr_size[0]:
                self.rect.right = 0
            elif self.rect.right < 0:
                self.rect.left = scr_size[0] - 2
            if self.rect.top >= scr_size[1]:
                self.rect.bottom = 0
            elif self.rect.bottom < 0:
                self.rect.top = scr_size[1] - 2
        self.cpt = (self.cpt + 1) % 3

    def inv_speed(self):
        self.immunity = 128
        self.vx *= -1
        self.vy *= -1


class TinyWorldView(kengi.EvListener):
    RAD = 5

    def __init__(self, ref_mod, rocksm):
        super().__init__()
        self.curr_pos = ref_mod.get_scr_pos()
        self.ref_rocksm = rocksm
        self.curr_angle = ref_mod.orientation

    def on_paint(self, ev):
        ev.screen.fill(BG_COLOR)
        for rock_spr in self.ref_rocksm:
            ev.screen.blit(rock_spr.image, rock_spr.rect.topleft)
        for b in bullets:
            pygame.draw.circle(ev.screen, BULLET_COLOR, (b[0].x, b[0].y), 3, 0)

        self._draw_player(ev.screen)

    def on_player_changes(self, ev):
        self.curr_angle = ev.orientation
        self.curr_pos = ev.pos

    def _draw_rocks(self, refscreen):
        for rockinfo in self.ref_rocksm:
            pos = rockinfo.rect.topleft
            pygame.draw.circle(refscreen, SHIP_COLOR, pos, 25, 2)

    def _draw_player(self, surf):
        orientation = self.curr_angle
        pt_central = self.curr_pos
        tv = [
            Vector2(), Vector2(), Vector2()
        ]
        tv[0].from_polar((self.RAD * 1.25, math.degrees(orientation + (2.0 * math.pi / 3))))
        tv[1].from_polar((self.RAD * 3, math.degrees(orientation)))
        tv[2].from_polar((self.RAD * 1.25, math.degrees(orientation - (2.0 * math.pi / 3))))
        pt_li = [Vector2(*pt_central),
                 Vector2(*pt_central),
                 Vector2(*pt_central)]
        for i in range(3):
            pt_li[i] += tv[i]
        pygame.draw.polygon(surf, SHIP_COLOR, pt_li, 2)


class ShipCtrl(kengi.EvListener):
    def __init__(self, ref_mod, rocksm):
        super().__init__()
        self._ref_ship = ref_mod
        self._ref_rocks = rocksm
        self.last_tick = None
        self._horz = Vector2(1, 0)
        self._joystick_target = Vector2(0, 0)
        self.curr_thrust = 0
        self.curr_brake = 0

    def on_stickmotion(self, ev):
        if ev.side == 'left':
            self._joystick_target.x, self._joystick_target.y = ev.pos

    def on_gamepaddown(self, ev):
        if 'A' == ev.button:
            self._ref_ship.shoot()

        elif ev.button == 'rTrigger':  # right trigger -> more speed
            if ev.value > 0.5:
                self.curr_thrust = 1
            else:
                self.curr_thrust = 0

        elif ev.button == 'lTrigger':
            if ev.value > 0.5:
                self.curr_brake = 1
            else:
                self.curr_brake = 0

    def on_keydown(self, ev):
        if ev.key == pygame.K_SPACE:
            self._ref_ship.shoot()

    def on_update(self, ev):
        global music_snd, game_obj
        ba = pygame.key.get_pressed()

        accel = stoppin = False
        if ba[pygame.K_UP]:
            accel = True
        if ba[pygame.K_DOWN]:
            stoppin = True
        if ba[pygame.K_RIGHT]:
            self._ref_ship.ccw_rotate()
        if ba[pygame.K_LEFT]:
            self._ref_ship.cw_rotate()

        if self.last_tick is not None:
            tmp = ev.curr_t - self.last_tick
        else:
            tmp = 0
        self.last_tick = ev.curr_t

        if self._joystick_target.length() > 0.44:
            self._ref_ship.interp_direction(math.radians(self._joystick_target.as_polar()[1]))

        if accel or self.curr_thrust > 0:
            self._ref_ship.accelerate(1.666)
        if stoppin or self.curr_brake > 0:
            self._ref_ship.brake(0.993)

        self._ref_ship.update(tmp)

        if len(self._ref_rocks):
            # there are rocks left in the space...
            for b in bullets:
                b[0].x += b[1].x
                b[0].y += b[1].y
            remove = set()
            rb = set()
            for elt in self._ref_rocks:
                for idx, b in enumerate(bullets):
                    if elt.rect.collidepoint((b[0].x, b[0].y)):
                        remove.add(elt)
                        elt.zombie = True
                        rb.add(idx)
                        break
                if not elt.zombie and not elt.immunity:
                    if elt.rect.collidepoint(self._ref_ship.pos):
                        elt.inv_speed()
                        self._ref_ship.reset()
                elt.update()
            if len(remove):
                for tmp in remove:
                    tmp.destroyed()
                    self._ref_rocks.remove(tmp)
                rbplus = list(rb)
                rbplus.sort(reverse=True)
                while len(rbplus) > 0:
                    del bullets[rbplus.pop()]
        else:  # proper exit
            music_snd.stop()
            game_obj.gameover = True


class IntroV(kengi.EvListener):
    OFFSET_START_BT_Y = 66
    OFFSET_ADDON_TXT_Y = 128
    LABELS_BINF_Y = 25

    def __init__(self):
        super().__init__()
        self.img = img_load('(astero)enter_start.png')
        self.dim = self.img.get_size()
        self.painting = True
        ft = pygame.font.Font(None, 21)
        txtcolor = 'antiquewhite2'
        self.labels = [ft.render(sline, False, txtcolor) for sline in INSTR.splitlines()]
        self.labels[0] = ft.render(INSTR.splitlines()[0], False, 'yellow')  # replace to have a title color
        self.gamepad_label = ft.render(LAST_LINE, False, txtcolor)

    def on_paint(self, ev):
        if self.painting:
            midpt_x = scr_size[0] // 2
            midpt_y = scr_size[1] // 2
            ev.screen.fill((11, 11, 11))
            for k, labl in enumerate(self.labels):
                ev.screen.blit(labl, (midpt_x-(labl.get_width()//2), self.LABELS_BINF_Y + 31*k))
            ev.screen.blit(
                self.img,
                (midpt_x-(self.img.get_width()//2), self.OFFSET_START_BT_Y + midpt_y)
            )
            ev.screen.blit(self.gamepad_label, (midpt_x-(self.gamepad_label.get_width()//2), midpt_y+self.OFFSET_ADDON_TXT_Y))

    def _begin_game(self):
        global music_snd
        self.painting = False
        pygame.mixer.init()
        music_snd = snd_load('(astero)ndimensions-zik.ogg')
        music_snd.set_volume(0.25)
        music_snd.play(-1)

    def on_gamepaddown(self, ev):
        if 'Start' == ev.button:
            self._begin_game()

    def on_keydown(self, ev):
        if ev.key == pygame.K_RETURN:
            self._begin_game()


class Astero(kengi.GameTpl):

    def init_video(self):
        kengi.init(2)

    def setup_ev_manager(self):
        self._manager.setup(MyEvTypes)

    def enter(self, vms=None):
        global scr_size
        super().enter(vms)
        scr_size[0], scr_size[1] = kengi.get_surface().get_size()
        shipm = ShipModel()
        li = [RockSprite() for _ in range(NB_ROCKS)]
        gcomponents = [
            TinyWorldView(shipm, li),
            ShipCtrl(shipm, li),
            IntroV()
        ]
        for compo in gcomponents:
            compo.turn_on()


game_obj = Astero()
# web
# katasdk.gkart_activation(game_obj)

game_obj.loop()
