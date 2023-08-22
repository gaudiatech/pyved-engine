import random

from .shooter import *
from .soundManager import *


class Ship(Shooter):
    # tune for small screen
    acceleration = 0.1
    decelaration = -0.0025
    maxVelocity = 7
    turnAngle = 5
    bulletVelocity = 8.0
    maxBullets = 3

    # acceleration = 0.2
    # decelaration = -0.005
    # maxVelocity = 10
    # turnAngle = 6
    # bulletVelocity = 13.0
    # maxBullets = 4

    SHIP_BULLET_TTL = 25

    def __init__(self, stage):
        position = Vector2d(stage.width / 2, stage.height / 2)
        heading = Vector2d(0, 0)
        self.thrustJet = ThrustJet(stage, self)
        self.shipDebrisList = []
        self.visible = True
        self.inHyperSpace = False
        pointlist = [(0, -10), (6, 10), (3, 7), (-3, 7), (-6, 10)]

        Shooter.__init__(self, position, heading, pointlist, stage)

    def draw(self):
        if self.visible:
            if not self.inHyperSpace:
                VectorSprite.draw(self)
            else:
                self.hyperSpaceTtl -= 1
                if self.hyperSpaceTtl == 0:
                    self.inHyperSpace = False
                    self.color = (255, 255, 255)
                    self.thrustJet.color = (255, 255, 255)
                    self.position.x = random.randrange(0, self.stage.width)
                    self.position.y = random.randrange(0, self.stage.height)
                    position = Vector2d(self.position.x, self.position.y)
                    self.thrustJet.position = position

        return self.transformedPointlist

    def rotate_left(self):
        self.angle += self.turnAngle
        self.thrustJet.angle += self.turnAngle

    def rotate_right(self):
        self.angle -= self.turnAngle
        self.thrustJet.angle -= self.turnAngle

    def increase_thrust(self):
        play_sound_continuous("thrust")
        if math.hypot(self.heading.x, self.heading.y) > self.maxVelocity:
            return

        dx = self.acceleration * math.sin(radians(self.angle)) * -1
        dy = self.acceleration * math.cos(radians(self.angle)) * -1
        self.change_velocity(dx, dy)

    def decrease_thrust(self):
        stop_sound("thrust")
        if (self.heading.x == 0 and self.heading.y == 0):
            return

        dx = self.heading.x * self.decelaration
        dy = self.heading.y * self.decelaration
        self.change_velocity(dx, dy)

    def change_velocity(self, dx, dy):
        self.heading.x += dx
        self.heading.y += dy
        self.thrustJet.heading.x += dx
        self.thrustJet.heading.y += dy

    def move(self):
        VectorSprite.move(self)
        self.decrease_thrust()

    # Break the shape of the ship down into several lines
    # Ship shape - [(0, -10), (6, 10), (3, 7), (-3, 7), (-6, 10)]    
    def explode(self):
        pointlist = [(0, -10), (6, 10)]
        self.add_ship_debris(pointlist)
        pointlist = [(6, 10), (3, 7)]
        self.add_ship_debris(pointlist)
        pointlist = [(3, 7), (-3, 7)]
        self.add_ship_debris(pointlist)
        pointlist = [(-3, 7), (-6, 10)]
        self.add_ship_debris(pointlist)
        pointlist = [(-6, 10), (0, -10)]
        self.add_ship_debris(pointlist)

    # Create a peice of ship debris
    def add_ship_debris(self, pointlist):#, color=None):
        heading = Vector2d(0, 0)
        position = Vector2d(self.position.x, self.position.y)
        #if color:
        tmp = pygame.Color('#ED7117')  # color orange
        debris = VectorSprite(position, heading, pointlist, (tmp[0],tmp[1],tmp[2]), angle=self.angle)
        #else:
        #debris = VectorSprite(position, heading, pointlist, self.angle)

        # Add debris to the stage
        self.stage.add_sprite(debris)

        # Calc a velocity moving away from the ship's center        
        centerX = debris.boundingRect.centerx
        centerY = debris.boundingRect.centery

        # Alter the random values below to change the rate of expansion
        debris.heading.x = ((centerX - self.position.x) + 0.1) / random.uniform(20, 40)
        debris.heading.y = ((centerY - self.position.y) + 0.1) / random.uniform(20, 40)
        self.shipDebrisList.append(debris)

    # Set the bullet velocity and create the bullet
    def fire_bullet(self):
        if self.inHyperSpace == False:
            vx = self.bulletVelocity * math.sin(radians(self.angle)) * -1
            vy = self.bulletVelocity * math.cos(radians(self.angle)) * -1
            heading = Vector2d(vx, vy)
            Shooter.fire_bullet(self, heading, self.SHIP_BULLET_TTL, self.bulletVelocity, "fire")

    def enter_hyper_space(self):
        if not self.inHyperSpace:
            self.inHyperSpace = True
            self.hyperSpaceTtl = 100
            self.color = (0, 0, 0)
            self.thrustJet.color = (0, 0, 0)


# Exhaust jet when ship is accelerating
class ThrustJet(VectorSprite):
    pointlist = [(-3, 7), (0, 13), (3, 7)]

    def __init__(self, stage, ship):
        position = Vector2d(stage.width / 2, stage.height / 2)
        heading = Vector2d(0, 0)
        self.accelerating = False
        self.ship = ship
        VectorSprite.__init__(self, position, heading, self.pointlist, (255, 255, 255))

    def draw(self):
        if self.accelerating and self.ship.inHyperSpace == False:
            self.color = (255, 255, 255)
        else:
            self.color = (0, 0, 0)

        VectorSprite.draw(self)
        return self.transformedPointlist
