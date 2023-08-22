#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

# import katagames_sdk as katasdk
# from . import b_astero
# b_astero.warmup()

import random

import sharedvars
from . import vars

katasdk = vars.katasdk = sharedvars.katasdk  # forward the ref to katasdk into the .vars, so other files below access it
from .soundManager import init_sound_manager, play_sound, stop_sound
from .vectorsprites import Vector2d
from .badies import Saucer, Rock, Debris
from .ship import Ship
from .stage import *


kengi = katasdk.kengi
pygame = kengi.pygame

DEBRIS_QUANT = 10  # 25
WARPBACK = [2, 'game_selector']


class AsteroidsGame(kengi.GameTpl):
    explodingTtl = 256

    def __init__(self):
        super().__init__()
        self.rockList = []
        self.saucer = None
        self.ship = None

    def init_video(self):
        kengi.init(2)

    def enter(self, vms=None):
        super().enter(vms)

        self.clock = pygame.time.Clock()
        self.frameCount = 0.0
        self.timePassed = 0.0

        init_sound_manager()

        self.stage = Stage('Pythentic Asteroids')
        self.paused = False
        self.frameAdvance = False
        self.gameState = 'attract'
        self.rockList = []
        self.secondsCount = 1
        self.score = 0
        self.lives = 0
        self.nextLife = 10000
        self.fps = 0.0

    def initialise_game(self):
        self.gameState = 'playing'
        [self.stage.remove_sprite(sprite) for sprite in self.rockList]  # clear old rocks
        if self.saucer is not None:
            self.kill_saucer()
        self.startLives = 3
        self.create_new_ship()
        self.create_lives_list()
        self.score = 0
        self.rockList = []
        self.numRocks = 3
        self.nextLife = 10000

        self.create_rocks(self.numRocks)
        self.secondsCount = 1

    def create_new_ship(self):
        if self.ship:
            [self.stage.spr_list.remove(debris) for debris in self.ship.shipDebrisList]
        self.ship = Ship(self.stage)
        self.stage.add_sprite(self.ship.thrustJet)
        self.stage.add_sprite(self.ship)

    def create_lives_list(self):
        self.lives += 1
        self.livesList = []
        for i in range(1, self.startLives):
            self.add_life(i)

    def add_life(self, lifeNumber):
        self.lives += 1
        ship = Ship(self.stage)
        self.stage.add_sprite(ship)
        ship_img_w = ship.boundingRect.width
        ship.position.x = self.stage.width - (lifeNumber * ship_img_w) - 10
        ship.position.y = 0 + ship.boundingRect.height
        self.livesList.append(ship)

    def create_rocks(self, numRocks):
        for _ in range(0, numRocks):
            position = Vector2d(random.randrange(-10, 10), random.randrange(-10, 10))

            newRock = Rock(self.stage, position, Rock.largeRockType)
            self.stage.add_sprite(newRock)
            self.rockList.append(newRock)

    def loop(self):
        self.enter()
        self.initialise_game()

        # Main loop                
        while not self.gameover:
            self.update(None)

    def update(self, infot):
        if self.gameover:
            return WARPBACK

        self.clock.tick(60)
        # fps
        # self.timePassed += self.clock.tick(60)
        # self.frameCount += 1
        # if self.frameCount % 10 == 0:
        #     self.fps = (self.frameCount / (self.timePassed / 1000.0))
        #     self.timePassed = 0
        #     self.frameCount = 0

        self.secondsCount += 1

        self.input(pygame.event.get())

        if self.paused and not self.frameAdvance:
            return

        self.stage.screen.fill((0, 0, 0))
        self.stage.move_sprites()
        self.stage.draw_sprites()
        self.do_saucer_logic()
        self.display_score()
        self.check_score()

        # self.display_fps()

        # Process keys
        if self.gameState == 'playing':
            self.playing()
        elif self.gameState == 'exploding':
            self.exploding()
        else:
            self.display_text()

        # Double buffer draw
        # pygame.display.flip()
        kengi.flip()

    def playing(self):
        if self.lives == 0:
            self.gameState = 'attract'
        else:
            self.process_keys()
            self.check_collisions()
            if len(self.rockList) == 0:
                self.level_up()

    def do_saucer_logic(self):
        if self.saucer is not None:
            if self.saucer.laps >= 2:
                self.kill_saucer()

        # Create a saucer, unless the game is on hold
        if (self.saucer is None) and self.gameState != 'attract':
            if self.secondsCount % 2000 == 0:
                randVal = random.randrange(0, 10)
                if randVal <= 3:
                    self.saucer = Saucer(self.stage, Saucer.smallSaucerType, self.ship)
                else:
                    self.saucer = Saucer(self.stage, Saucer.largeSaucerType, self.ship)
                self.stage.add_sprite(self.saucer)

    def exploding(self):
        self.explodingCount += 1
        for debris in self.ship.shipDebrisList:
            r, g, b = debris.color
            r = max(0, r - 1)
            g = max(0, r - 1)
            b = max(0, r - 1)
            debris.color = (r, g, b)

        if self.explodingCount > self.explodingTtl:
            self.gameState = 'playing'
            [self.stage.spr_list.remove(debris) for debris in self.ship.shipDebrisList]
            self.ship.shipDebrisList = []

            if self.lives == 0:
                self.ship.visible = False
            else:
                self.create_new_ship()

    def level_up(self):
        self.numRocks += 1
        self.create_rocks(self.numRocks)

    def display_text(self):
        font1 = pygame.font.Font(None, 34)
        titleText = font1.render('Astero', False, (255, 255, 255))
        titleTextRect = titleText.get_rect(centerx=self.stage.width / 2)
        titleTextRect.y = self.stage.height / 2 - titleTextRect.height * 2
        self.stage.screen.blit(titleText, titleTextRect)

        font2 = pygame.font.Font(None, 16)
        keysText = font2.render(
            'Controls: arrow keys left, right, thrust | Space: fire, H: hyperspace, Esc: Quit', True,
            (255, 255, 255))
        #keysTextRect = keysText.get_rect(centerx=self.stage.width / 2)
        #keysTextRect.y = self.stage.height / 2 - keysTextRect.height / 2
        tw, th = keysText.get_size()
        scrw, scrh = kengi.get_surface().get_size()
        self.stage.screen.blit(
            keysText,
            (20+int((scrw-tw)/2), int((scrh-th)/2))
            #(scrw/2 - tw/2, scrh/2-scrh/2)
        )

        keysText = font2.render('Alternative: Z left, X right, N thrust | M: fire, H: hyperspace, Esc: Quit', True,
                                (255, 255, 255))
        # keysTextRect = keysText.get_rect(centerx=self.stage.width / 2)
        # keysTextRect.y = self.stage.height / 2 + keysTextRect.height / 2
        tw, th = keysText.get_size()
        self.stage.screen.blit(keysText, (20+int((scrw-tw)/2), 33+int((scrh-th)/2)))

        instructionText = font1.render('Press Enter To Play', False, pygame.Color('#D67229'))#(255, 255, 255))
        instructionTextRect = instructionText.get_rect(centerx=self.stage.width / 2)
        instructionTextRect.y = self.stage.height / 2 + instructionTextRect.height * 2
        self.stage.screen.blit(instructionText, instructionTextRect)

    def display_score(self):
        font2 = pygame.font.Font(None, 30)
        scoreStr = str("%06d" % self.score)
        scoreText = font2.render(scoreStr, True, (255, 255, 255))
        scoreTextRect = scoreText.get_rect(centerx=40, centery=15)
        self.stage.screen.blit(scoreText, scoreTextRect)

    def display_fps(self):
        font2 = pygame.font.Font(None, 15)
        fpsStr = str(int(self.fps))
        scoreText = font2.render(fpsStr, True, (128, 128, 128))
        scoreTextRect = scoreText.get_rect(centerx=(self.stage.width / 2), centery=15)
        self.stage.screen.blit(scoreText, scoreTextRect)

    def display_paused(self):
        if self.paused:
            font2 = pygame.font.Font(None, 30)
            pausedText = font2.render("Paused", True, (255, 255, 255))
            textRect = pausedText.get_rect(centerx=self.stage.width / 2, centery=self.stage.height / 2)
            self.stage.screen.blit(pausedText, textRect)
            pygame.display.update()

    # Should move the ship controls into the ship class
    def input(self, events):
        self.frameAdvance = False
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.gameover = True

                if self.gameState == 'playing':
                    if event.key == pygame.K_SPACE:
                        self.ship.fire_bullet()
                    elif event.key == pygame.K_n:
                        self.ship.fire_bullet()
                    elif event.key == pygame.K_h:
                        self.ship.enter_hyper_space()

                elif self.gameState == 'attract':
                    # Start a new game
                    if event.key == pygame.K_RETURN:
                        self.initialise_game()

                if event.key == pygame.K_p:
                    if self.paused:
                        self.paused = False
                    else:
                        self.paused = True

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_o:
                    self.frameAdvance = True

    def process_keys(self):
        key = pygame.key.get_pressed()

        if key[pygame.K_LEFT] or key[pygame.K_z]:
            self.ship.rotate_left()
        elif key[pygame.K_RIGHT] or key[pygame.K_x]:
            self.ship.rotate_right()

        if key[pygame.K_UP] or key[pygame.K_m]:
            self.ship.increase_thrust()
            self.ship.thrustJet.accelerating = True
        else:
            self.ship.thrustJet.accelerating = False

    # Check for ship hitting the rocks etc.
    def check_collisions(self):

        # Ship bullet hit rock?
        newRocks = []
        shipHit, saucerHit = False, False

        # Rocks
        for rock in self.rockList:
            rockHit = False

            if not self.ship.inHyperSpace and rock.collidesWith(self.ship):
                p = rock.check_polygon_collision(self.ship)
                if p is not None:
                    shipHit = True
                    rockHit = True

            if self.saucer is not None:
                if rock.collidesWith(self.saucer):
                    saucerHit = True
                    rockHit = True

                if self.saucer.bullet_collision(rock):
                    rockHit = True

                if self.ship.bullet_collision(self.saucer):
                    saucerHit = True
                    self.score += self.saucer.scoreValue

            if self.ship.bullet_collision(rock):
                rockHit = True

            if rockHit:
                self.rockList.remove(rock)
                self.stage.spr_list.remove(rock)

                if rock.rockType == Rock.largeRockType:
                    play_sound("explode1")
                    newRockType = Rock.mediumRockType
                    self.score += 50
                elif rock.rockType == Rock.mediumRockType:
                    play_sound("explode2")
                    newRockType = Rock.smallRockType
                    self.score += 100
                else:
                    play_sound("explode3")
                    self.score += 200
                    newRockType = None

                if rock.rockType != Rock.smallRockType:
                    # new rocks
                    for _ in range(0, 2):
                        position = Vector2d(rock.position.x, rock.position.y)
                        newRock = Rock(self.stage, position, newRockType)
                        self.stage.add_sprite(newRock)
                        self.rockList.append(newRock)

                self.create_debris(rock)

        # Saucer bullets
        if self.saucer is not None:
            if not self.ship.inHyperSpace:
                if self.saucer.bullet_collision(self.ship):
                    shipHit = True

                if self.saucer.collidesWith(self.ship):
                    shipHit = True
                    saucerHit = True

            if saucerHit:
                self.create_debris(self.saucer)
                self.kill_saucer()

        if shipHit:
            self.kill_ship()

    def kill_ship(self):
        stop_sound("thrust")
        play_sound("explode2")
        self.explodingCount = 0
        self.lives -= 1
        if (self.livesList):
            ship = self.livesList.pop()
            self.stage.remove_sprite(ship)

        self.stage.remove_sprite(self.ship)
        self.stage.remove_sprite(self.ship.thrustJet)
        self.gameState = 'exploding'
        self.ship.explode()

    def kill_saucer(self):
        stop_sound("lsaucer")
        stop_sound("ssaucer")
        play_sound("explode2")
        self.stage.remove_sprite(self.saucer)
        self.saucer = None

    def create_debris(self, sprite):
        for _ in range(DEBRIS_QUANT):
            position = Vector2d(sprite.position.x, sprite.position.y)
            debris = Debris(position, self.stage)
            self.stage.add_sprite(debris)

    def check_score(self):
        if self.score > 0 and self.score > self.nextLife:
            play_sound("extralife")
            self.nextLife += 10000
            self.add_life(self.lives)


game = AsteroidsGame()
# game.loop()
katasdk.gkart_activation(game)
