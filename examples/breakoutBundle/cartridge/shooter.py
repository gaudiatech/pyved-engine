from .vectorsprites import *
from .soundManager import *


class Shooter(VectorSprite):    
    
    def __init__(self, position, heading, pointlist, stage):
        VectorSprite.__init__(self, position, heading, pointlist, (255,255,255))
        self.bullets = []        
        self.stage = stage
    
    def fire_bullet(self, heading, ttl, velocity, shoot_sound):
        if (len(self.bullets) < self.maxBullets):                          
            position = Vector2d(self.position.x, self.position.y)
            newBullet = Bullet(position, heading, self, ttl, velocity, self.stage)
            self.bullets.append(newBullet)
            self.stage.add_sprite(newBullet)
            play_sound(shoot_sound)

    def bullet_collision(self, target):
        collisionDetected = False
        for bullet in self.bullets:
            if bullet.ttl > 0 and target.collidesWith(bullet):
                collisionDetected = True
                bullet.ttl = 0
        
        return collisionDetected

class Bullet(Point):
    
    def __init__(self, position, heading, shooter, ttl, velocity, stage):
        Point.__init__(self, position, heading, stage)
        self.shooter = shooter
        self.ttl = ttl
        self.velocity = velocity
        
    def move(self):
        Point.move(self)
        if (self.ttl <= 0): 
            self.shooter.bullets.remove(self)        
