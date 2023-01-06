import math
import random
import time

import katagames_engine as kengi


kengi.bootstrap_e()  # so pygame can be used rn


# game constants
BG_COLOR = (0, 25, 0)
SHIP_COLOR = (119, 255, 0)
BULLET_COLOR = SHIP_COLOR
NB_ROCKS = 3

pygame = kengi.pygame
CogObject = kengi.event2.Emitter
EventReceiver = kengi.event2.EvListener
EngineEvTypes = kengi.event2.EngineEvTypes
bullets = list()
scr_size = [0, 0]
music_snd = None
view = ctrl = None
Vector2 = pygame.math.Vector2

MyEvTypes = kengi.game_events_enum((
    'PlayerChange',  # contains: new_pos, angle
    'PlayerstateChange'
))

lu_event = p_event = None


def img_load(img_name):
    return pygame.image.load(img_name)


def snd_load(path):
    return pygame.mixer.Sound(path)


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


class ShipModel(kengi.event2.Emitter):
    MISSILE_SPEED = 3
    SPEED_CAP = 192
    THRUST_VAL = 0.823
    DELTA_ANGLE = 0.051

    def __init__(self):
        super().__init__()
        self.scr_size = sw, sh = kengi.vscreen.get_screen().get_size()

        # instantanné
        self._position = Vector2(sw // 2, sh // 2)
        self._orientation = Vector2(1, 0)

        # vitesse variable
        self._curr_speed = 0.0  # can be negative too

    def reset(self):
        self._position[:] = (scr_size[0] // 2, scr_size[1] // 2)
        self._orientation[:] = (1, 0)
        self._curr_speed = 0.0
        # only new state & stats

        self.pev(MyEvTypes.PlayerstateChange, orientation=self.orientation, speed=self._curr_speed)
        self.pev(MyEvTypes.PlayerChange, pos=self.pos, orientation=self.orientation)

    @property
    def pos(self):
        return self._position.x, self._position.y

    @property
    def orientation(self):
        return self._orientation.as_polar()[1]  # returns a value in RAD

    def _clamp_n_broadcast_state(self):
        xcap, ycap = self.scr_size

        if self._position.x < 0:
            self._position.x = xcap + self._position.x
        if self._position.x > xcap:
            self._position.x = self._position.x - xcap
        if self._position.y < 0:
            self._position.y = ycap + self._position.y
        if self._position.y > ycap:
            self._position.y = self._position.y - ycap

        self.pev(MyEvTypes.PlayerChange, pos=self.pos, orientation=self.orientation)

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
        self.pev(MyEvTypes.PlayerstateChange, orientation=b, speed=self._curr_speed)
        self._clamp_n_broadcast_state()

    def cw_rotate(self):
        _, b = self._orientation.as_polar()
        b -= self.DELTA_ANGLE
        self._orientation.from_polar((1, b))
        self.pev(MyEvTypes.PlayerstateChange, orientation=b, speed=self._curr_speed)
        self._clamp_n_broadcast_state()

    def interp_direction(self, given_or):
        # find how to multiply g_or before we compare (+/- 2 pi)
        self._orientation.from_polar((1, given_or))
        self.pev(MyEvTypes.PlayerstateChange, orientation=given_or, speed=self._curr_speed)
        self._clamp_n_broadcast_state()

    def accelerate(self, v):
        tmp = self._curr_speed + self.THRUST_VAL * (v+1)
        if tmp <= self.SPEED_CAP:
            self._curr_speed = tmp
            _, b = self._orientation.as_polar()
            self.pev(MyEvTypes.PlayerstateChange, orientation=b, speed=self._curr_speed)
            self._clamp_n_broadcast_state()

    def brake(self, v):
        if self._curr_speed <= 0:
            return
        tmp = self._curr_speed - (1.97+v)
        if tmp < 1:
            self._curr_speed = 0
        else:
            self._curr_speed = tmp
        _, b = self._orientation.as_polar()
        self.pev(MyEvTypes.PlayerstateChange, orientation=b, speed=self._curr_speed)

    def shoot(self):
        global bullets
        sh_pos = Vector2(self.pos)
        b_speed = Vector2()
        b_speed.from_polar((self.MISSILE_SPEED, math.degrees(self.orientation)))
        bullets.append((sh_pos, b_speed))

    def get_scr_pos(self):
        return int(self._position.x), int(self._position.y)


class TinyWorldView(EventReceiver):
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

    # we could disp. the info like Headup display...?
    #
    # def on_playerstate_change(self, ev):
    #     print('new speed', ev.speed)
    #     print('new orientation', ev.orientation)

    def on_player_change(self, ev):
        self.curr_angle = ev.orientation
        self.curr_pos = ev.pos

    def _draw_rocks(self, refscreen):
        for rockinfo in self.ref_rocksm:
            pos = rockinfo.rect.topleft
            pygame.draw.circle(refscreen, SHIP_COLOR, pos, 25, 2)

    def _draw_player(self, surf):
        orientation = self.curr_angle
        pt_central = self.curr_pos
        # pygame.draw.circle(surf, SHIP_COLOR, pt_central, 13)
        # return
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
        # pt_li.reverse()
        pygame.draw.polygon(surf, SHIP_COLOR, pt_li, 2)


class ShipCtrl(EventReceiver):
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
        if ev.axis == 5:  # right trigger
            if ev.value > 0.:
                self.curr_thrust = ev.value
            else:
                self.curr_thrust = 0

        elif ev.axis == 4:  # left trigger
            if ev.value > 0.:
                self.curr_brake = ev.value
            else:
                self.curr_brake = 0

        elif ev.axis == 0:
            self._joystick_target.x = ev.value

        elif ev.axis == 1:
            self._joystick_target.y = -ev.value

    def on_gamepaddown(self, ev):
        if 'A' == ev.button:
            self._ref_ship.shoot()

    def on_update(self, ev):
        global music_snd, game_obj

        if self._joystick_target.length() > 0.44:
            self._ref_ship.interp_direction(-math.radians(self._joystick_target.as_polar()[1]))

        ba = pygame.key.get_pressed()
        if ba[pygame.K_UP]:
            self.curr_thrust = 0.75
        if ba[pygame.K_DOWN]:
            self.curr_brake = 0.77
        if ba[pygame.K_RIGHT]:
            self._ref_ship.ccw_rotate()
        if ba[pygame.K_LEFT]:
            self._ref_ship.cw_rotate()

        if self.curr_brake > 0:
            self._ref_ship.brake(self.curr_brake)
        else:
            if self.curr_thrust > 0:
                self._ref_ship.accelerate(self.curr_thrust)

        # handle bullets
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

        if len(self._ref_rocks) == 0:
            # clean de-pop game
            music_snd.stop()
            game_obj.gameover = True
            return

        # update ship state/pos
        if not(hasattr(self, '_last_t')) or (self._last_t is None):
            delta = 0
        else:
            delta = ev.curr_t - self._last_t
        self._last_t = ev.curr_t
        self._ref_ship.update(delta)

    def on_keydown(self, ev):
        if ev.key == pygame.K_SPACE:
            self._ref_ship.shoot()
        elif ev.key == pygame.K_RETURN:
            print(self._ref_ship.pos)
            print(self._ref_ship.orientation)


def print_mini_tutorial():
    howto_infos = """HOW TO PLAY:
    * use arrows to move
    * use SPACE to shoot"""
    print('-' * 32)
    for line in howto_infos.split('\n'):
        print(line)
    print('-' * 32)


class IntroV(EventReceiver):
    def __init__(self):
        super().__init__()
        self.img = img_load('(astero)enter_start.png')
        self.dim = self.img.get_size()
        self.intro_state = True

    def on_paint(self, ev):
        if self.intro_state:
            ev.screen.fill((0, 0, 0))
            ev.screen.blit(self.img, ((scr_size[0] - self.dim[0]) // 2, (scr_size[1] - self.dim[1]) // 2))

    def _begin_game(self):
        global music_snd
        pygame.mixer.init()
        music_snd = snd_load('(astero)ndimensions-zik.ogg')
        music_snd.set_volume(0.25)
        music_snd.play(-1)
        self.intro_state = False

    def on_gamepaddown(self, ev):
        if self.intro_state and ev.button == 'Start':
            self._begin_game()

    def on_keydown(self, ev):
        if self.intro_state and ev.key == pygame.K_RETURN:
            self._begin_game()


class AsteroGame(kengi.GameTpl):

    def enter(self, vmstate=None):
        global scr_size, view, ctrl, lu_event, p_event

        kengi.init(2)
        self._manager = kengi.get_ev_manager()
        self._manager.setup(MyEvTypes)

        scr_size[0], scr_size[1] = kengi.get_surface().get_size()
        introv = IntroV()
        shipm = ShipModel()
        li = [RockSprite() for _ in range(NB_ROCKS)]
        view = TinyWorldView(shipm, li)
        ctrl = ShipCtrl(shipm, li)
        view.turn_on()
        ctrl.turn_on()
        introv.turn_on()
        game_ctrl = kengi.get_game_ctrl()
        game_ctrl.turn_on()

    def exit(self, vmstate=None):
        self._manager.update()  # flush events
        kengi.quit()


game_obj = AsteroGame()

if __name__ == '__main__':
    print_mini_tutorial()
    game_obj.loop()
