import random
import time

from . import pimodules


# -ALIASES-
pyv = pimodules.pyved_engine
pyv.bootstrap_e()  # hence we can use pyv.pygame before a pyv.init() call
pygame = pyv.pygame

# -CONSTANTS-
NXT_GAME = 'game_selector'
FPS = 60
Y_COORD_GROUND = 427
X_HB2 = 530
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

WARRIOR_SIZE = 162
WARRIOR_SCALE = 4
WARRIOR_OFFSET = [72, 56]
WARRIOR_DATA = [WARRIOR_SIZE, WARRIOR_SCALE, WARRIOR_OFFSET]
WIZARD_SIZE = 250
WIZARD_SCALE = 3
WIZARD_OFFSET = [112, 107]
WIZARD_DATA = [WIZARD_SIZE, WIZARD_SCALE, WIZARD_OFFSET]
WARRIOR_ANIMATION_STEPS = [10, 8, 1, 7, 7, 3, 7]  # def. number of steps in each animation
WIZARD_ANIMATION_STEPS = [8, 8, 1, 8, 8, 3, 7]

ROUND_OVER_COOLDOWN = 2  # sec
NB_SEC_INTRO_COMBAT = 3

# TODO gameplay fixes:
#  chrono devrait se ré-afficher a chaque round
#  "best of 3" rule


# ---------------------------------------
#  Code pour le jeu de combat (O.O.P.)
# ---------------------------------------
class Fighter:
    # class const
    XSPEED = 25
    YSPEED = 66
    ANIM_FREQ = 0.04140  # the lowest, the faster the char. animation is

    def __init__(self, player, x, y, flip, data, sprite_sheet_info, animation_steps, sound, scr_size):
        self.scr_size = scr_size
        self.ai_control = False
        self.ai_wait = 230
        self.run_duration = 0
        self.player = player
        self.size = data[0]
        self.image_scale = data[1]
        self.offset = data[2]
        self.flip = flip

        # list of pygame surfaces
        self.animation_list = self.load_images(sprite_sheet_info, animation_steps)

        self.action = 0  # 0:idle #1:run #2:jump #3:attack1 #4: attack2 #5:hit #6:death
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.update_time = None
        self.rect = pygame.Rect((x, y, 80, 180))

        self.vx = 0
        self.vy = 0

        self.running = False
        self.jump = False
        self.attacking = False
        self.attack_type = None
        self.attack_cooldown = 0
        self.attack_sound = sound
        self.hit = False
        self.health = 100
        self.alive = True

    def load_images(self, sprsheet_infos, animsteps):
        print(sprsheet_infos)
        spr_sheet_name = sprsheet_infos[1]  # pyv.gfx.JsonBasedSprSheet(sprsheet_path)
        sprsheet_obj = pyv.vars.spritesheets[spr_sheet_name]

        arg_scale = (self.size * self.image_scale, self.size * self.image_scale)
        res = list()
        for k, nbframes in enumerate(animsteps):
            tmp = list()
            for anim_rank in range(nbframes):
                img_name = 'a' + str(k) + str(anim_rank) + '.png'
                surf_obj = pygame.transform.scale(sprsheet_obj[img_name], arg_scale)
                tmp.append(surf_obj)
            res.append(tmp)
        return res

    def move(self, screen_width, screen_height, surface, target, activematch):
        if not activematch or (not self.alive):
            return

        # TODO remove dependency control keys->logic
        pkeys = pygame.key.get_pressed()
        # modify speeds:
        if pkeys[pygame.K_UP]:
            if not self.jump:
                self.jump = True
                self.vy = -1 * self.YSPEED
        if pkeys[pygame.K_RIGHT]:
            self.vx = +1 * self.XSPEED
            self.running = True
        elif pkeys[pygame.K_LEFT]:
            self.vx = -1 * self.XSPEED
            self.running = True
        else:
            self.vx = 0
            self.running = False

        # modify fighter state.
        attack_key0 = pygame.K_SPACE
        attack_key1 = pygame.K_x
        if not self.attacking:
            if pkeys[attack_key0]:
                self.attack_type = 0
            elif pkeys[attack_key1]:
                self.attack_type = 1
            if self.attack_type in (0, 1):
                self.attacking = True
                self.attack(target)

        return  # -------------------- below is bugged code ------------

        # attack keycodes


        # can only perform other actions if not currently attacking
        if not self.attacking:
            # check player 1 controls
            if self.player == 2 and (not self.ai_control):
                # movement
                if key[pygame.K_a]:
                    dx = -self.SPEED_X
                    self.running = True
                if key[pygame.K_u]:
                    dx = self.SPEED_X
                    self.running = True
                # jump
                if key[pygame.K_w] and not self.jump:
                    self.vx = self.SPEED_Y
                    self.jump = True
                # attack
                if key[pygame.K_r] or key[pygame.K_t]:
                    self.attack(target)
                    # determine which attack type was used
                    if key[pygame.K_r]:
                        self.attack_type = 1
                    if key[pygame.K_t]:
                        self.attack_type = 2

            # check player 2 controls
            if self.player == 1:
                # movement
                if key[pygame.K_RIGHT]:
                    dx = self.SPEED_X
                    self.running = True

                if key[pygame.K_LEFT]:
                    dx = -self.SPEED_X
                    self.running = True

                # jump
                if key[pygame.K_UP]:
                    if not self.jump:
                        self.vel_y = self.JUMP_UP_VELOCITY
                        self.jump = True

                if key[keycode0] or key[keycode1]:
                    self.attack(target)
                    # determine which attack type was used
                    if key[keycode0]:
                        self.attack_type = 1
                    elif key[keycode1]:
                        self.attack_type = 2

        # apply gravity
        if self.jump:
            dy = self.vel_y = self.vel_y + self.GRAVITY
        else:
            dy = 0

        # apply attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        self.rect.left += dx
        if dy:
            self.rect.top += dy

        # TODO debug!
        # if not self.ai_control:
        #    self._ensure_screen_boundaries(dx, dy, target)

    # def _ensure_screen_boundaries(self, dx, dy, targ):
    #     screen_width, screen_height = self.scr_size
    #     # ensure player stays on screen
    #     if self.rect.left + dx < 0:
    #         dx = -self.rect.left
    #     if self.rect.right + dx > screen_width:
    #         dx = screen_width - self.rect.right
    #     if self.rect.bottom + dy > screen_height - 110:
    #         self.vel_y = 0
    #         self.jump = False
    #         dy = screen_height - 110 - self.rect.bottom
    #
    #     # update player position
    #     self.rect.x += dx
    #     self.rect.y += dy
    #
    #     # ensure players face each other
    #     if targ.rect.centerx > self.rect.centerx:
    #         self.flip = False
    #         targ.flip = True
    #     else:
    #         self.flip = True
    #         targ.flip = False

    def close_dist(self, other_f):
        attacking_rect = pygame.Rect(self.rect.centerx - (2 * self.rect.width * self.flip), self.rect.y,
                                     2 * self.rect.width, self.rect.height)
        return attacking_rect.colliderect(other_f.rect)

    def play_ai(self):
        return
        # TODO fix the AI opponent!
        global fighter_1, intro_count, round_over
        enemy = fighter_1

        if (not self.alive) or (intro_count > 0) or round_over:
            return  # dont cheat!
        self.ai_wait -= 3
        if self.ai_wait > 0:
            return

        if self.run_duration > 0:
            if abs(enemy.rect.centerx - self.rect.centerx) < 48:
                self.run_duration = -1
                return
            self.run_duration -= 2
            self.running = True
            if self.rect.centerx < enemy.rect.centerx:
                dx = self.SPEED_X
            else:
                dx = -self.SPEED_X
            self._ensure_screen_boundaries(dx, 0, enemy)
            return
        self.running = False
        if random.random() < 0.05:
            print('AI: decides to wait')
            self.ai_wait = random.randint(47, 134)
            return

        if not self.attacking:
            if abs(enemy.rect.centerx - self.rect.centerx) > 380:
                self.run_duration = random.randint(34, 54)
                return
            if random.random() < 0.4:
                return
            self.attack(enemy)
            self.attack_type = random.choice((1, 2))

    # handle animation updates
    def update(self):
        # update y speed
        if self.jump:
            self.vy += 0.085 * self.YSPEED
            if self.vy < 0:
                if abs(self.vy) < 0.24*self.YSPEED:
                    self.vy *= -1  # at some point, start to fall down

        # update pos and fighter state
        self.rect.x += self.vx
        self.rect.top += self.vy
        if self.health <= 0:
            self.health = 0
            self.alive = False

        # handle: landing /stop jumping
        if self.jump and self.rect.top > Y_COORD_GROUND:
            self.rect.top = Y_COORD_GROUND
            self.jump = False
            self.vy = 0

        # check what action the player is performing
        # if self.health <= 0:
        #     self.health = 0
        #     self.alive = False
        #     self.update_action(6)  # 6:death
        # elif self.hit:
        #     self.update_action(5)  # 5:hit
        #
        #
        # elif self.jump:
        #     self.update_action(2)  # 2:jump

        # -----------
        #  animating char.
        # -----------
        if self.attack_type == 0:
            self.update_action(3)  # code 3 => attack primary
        elif self.attack_type == 1:
            self.update_action(4)  # code4 => attack secondary
        elif self.running:
            self.update_action(1)  # code1 => just run
        elif not self.alive:
            self.update_action(6)  # death
        else:
            self.update_action(0)  # code0 => idle char.

        # update the image
        self.image = self.animation_list[self.action][self.frame_index]
        curr_t = time.time()
        # check if enough time has passed since the last update
        if (self.update_time is None) or (curr_t - self.update_time) > self.ANIM_FREQ:
            self.frame_index += 1
            self.update_time = curr_t
        # check if the animation has finished
        if self.frame_index >= len(self.animation_list[self.action]):

            if not self.alive:
                self.frame_index = len(self.animation_list[self.action]) - 1  # if the player is dead then end the animation

            else:
                self.frame_index = 0
                # check if an attack was executed
                if self.action == 3 or self.action == 4:
                    self.attacking = False
                    self.attack_type = None
                    # logic:
                    # self.attack_cooldown = 20 / 100

                # anim of damage-taken finishes
                elif self.action == 5:
                    self.hit = False
                    # if the player was in the middle of an attack, then the attack is stopped
                    self.attacking = False
                    self.attack_cooldown = 20 / 100

    def attack(self, target):
        if self.attack_cooldown <= 0:
            # execute attack
            self.attacking = True
            self.attack_sound.play()
            attacking_rect = pygame.Rect(self.rect.centerx - (2 * self.rect.width * self.flip), self.rect.y,
                                         2 * self.rect.width, self.rect.height)
            if attacking_rect.colliderect(target.rect):
                target.health -= 10
                target.hit = True

    def update_action(self, new_action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            self.update_time = time.time()

    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(
            img,
            (self.rect.x - (self.offset[0] * self.image_scale), self.rect.y - (self.offset[1] * self.image_scale))
        )


# -GLOBAL VARIABLES-
clock = None
fighter_1 = fighter_2 = None

last_count_update = None
magic_fx = sword_fx = None
round_over = False
round_over_time = None
drawing_counter = True
intro_count = 0
score = [0, 0]  # player scores. [P1, P2]
score_font = count_fount = None
victory_img = defeat_img = None
lastupdate = None
screen = None


# ---------------------------------------
#  Code pour le jeu de combat (non-O.O.P.)
# ---------------------------------------
def draw_health_bar(health, x, y):
    ratio = health / 100
    pygame.draw.rect(screen, WHITE, (x - 2, y - 2, 404, 34))
    pygame.draw.rect(screen, RED, (x, y, 400, 30))
    pygame.draw.rect(screen, YELLOW, (x, y, 400 * ratio, 30))


def draw_text(text, font, text_col, x, y):  # function for drawing text
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def reset_fighters():
    global fighter_1, fighter_2
    fighter_1 = Fighter(
        1, 200, Y_COORD_GROUND, False, WARRIOR_DATA, (None, 'warrior-spritesheet'), WARRIOR_ANIMATION_STEPS, sword_fx,
        pyv.get_surface().get_size()
    )
    fighter_1.attack_sound = sword_fx
    fighter_2 = Fighter(
        2, 700, Y_COORD_GROUND, True, WIZARD_DATA, (None, 'sorc-spritesheet'), WIZARD_ANIMATION_STEPS, magic_fx,
        pyv.get_surface().get_size()
    )
    fighter_2.attack_sound = magic_fx
    fighter_2.ai_control = True


@pyv.declare_begin
def initgame(vms=None):
    global fighter_1, fighter_2, intro_count, magic_fx, sword_fx
    global last_count_update, clock, screen
    global victory_img, defeat_img, count_font, score_font

    pyv.init()
    screen = pyv.get_surface()
    # screen = pyv.get_surface()

    # pyv.preload_assets({
    #     "assets": ["bg.png", "victory.png", "defeat.png"],
    #     "sounds": ["immortal-sword.wav", "immortal-magic.wav"]
    # }, prefix_asset_folder='cartridge/')

    # +++ load music and sounds +++
    # pygame.mixer.music.load(assetprefix("music.mp3"))
    # pygame.mixer.music.play(-1)
    sword_fx = pyv.vars.sounds["immortal-sword"]
    magic_fx = pyv.vars.sounds["immortal-magic"]

    # completion fighter objects
    wh_pair = pyv.get_surface().get_size()

    # verif fighters sont bien construits
    reset_fighters()
    fighter_1.attack_sound = sword_fx
    fighter_1.scr_size = fighter_2.scr_size = wh_pair
    fighter_2.attack_sound = magic_fx
    fighter_2.ai_control = True

    last_count_update = time.time()
    clock = pyv.vars.clock

    # load background image
    bg_image = pyv.vars.images['bg'].convert_alpha()

    # load spritesheets
    # warrior_sheet = pygame.image.load(assetprefix("warrior.png")).convert_alpha()
    # wizard_sheet = pygame.image.load(assetprefix("wizard.png")).convert_alpha()

    # load vicory image
    victory_img = pyv.vars.images["victory"].convert_alpha()
    defeat_img = pyv.vars.images["defeat"].convert_alpha()

    # define font
    # TODO pb a resourdre avant de passer vers le Web ctx: comment les fonts sont importées?
    count_font = pyv.vars.fonts['bigFont']
    score_font = pyv.vars.fonts['smaFont']

    # init. logic
    intro_count = NB_SEC_INTRO_COMBAT


@pyv.declare_update
def updategame(infot):
    global lastupdate
    global score_font, fighter_1, fighter_2, last_count_update, round_over
    global intro_count, round_over_time, magic_fx, sword_fx, drawing_counter

    if lastupdate is None:
        dt = 0
    else:
        dt = lastupdate - infot
    lastupdate = infot

    # event handler
    for ev in pyv.fetch_events():
        if ev.type == pygame.QUIT:
            pyv.vars.gameover = True
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                pyv.vars.gameover = True
            elif ev.key == pygame.K_BACKSPACE:
                fighter_2.ai_control = False

    # ---------------
    #  LOGIC
    # ---------------
    scr_w, scr_h = screen.get_size()

    # update countdown
    if drawing_counter and (infot - last_count_update) > 1.0:
        intro_count -= 1
        last_count_update = infot
    if drawing_counter and intro_count < 1:
        drawing_counter = False

    if not drawing_counter:
        fighter_1.move(scr_w, scr_h, screen, fighter_2, not round_over)

    if fighter_2.ai_control:
        fighter_2.play_ai()
    else:
        fighter_2.move(scr_w, scr_h, screen, fighter_1, not round_over)

    # update fighters
    fighter_1.update()
    fighter_2.update()

    # check for player defeat
    if not round_over:
        if not fighter_1.alive:
            score[1] += 1
            round_over_time = infot
            round_over = True
        elif not fighter_2.alive:
            score[0] += 1
            round_over_time = infot
            round_over = True

    else:  # we have to reset match
        if (infot - round_over_time) > ROUND_OVER_COOLDOWN:
            round_over = False
            intro_count = NB_SEC_INTRO_COMBAT
            reset_fighters()
            # fighter_1 = Fighter(1, 200, SPAWN_Y, False, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
            # fighter_2 = Fighter(2, 700, SPAWN_Y, True, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)

    # draw background
    screen.blit(pyv.vars.images['bg'], (0, 0))

    if round_over:
        if fighter_1.alive:
            # display victory simage
            screen.blit(victory_img, (360, 150))
        else:
            screen.blit(defeat_img, (360, 150))

    elif drawing_counter:
        # display count timer
        scr_w, scr_h = screen.get_size()
        draw_text(str(intro_count), count_font, RED, scr_w / 2, scr_h / 3)

    # show player stats
    draw_health_bar(fighter_1.health, 20, 20)
    draw_health_bar(fighter_2.health, X_HB2, 20)
    draw_text("P1: " + str(score[0]), score_font, RED, 20, 60)
    draw_text("P2: " + str(score[1]), score_font, RED, X_HB2, 60)

    # draw fighters
    fighter_1.draw(screen)
    fighter_2.draw(screen)

    # update display
    pyv.flip()
    clock.tick(FPS)


@pyv.declare_end
def exitgame(vms=None):
    # exit pygame
    pyv.quit()
