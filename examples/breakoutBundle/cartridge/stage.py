
from . import vars
katasdk = vars.katasdk
pygame = katasdk.kengi.pygame
kengi = katasdk.kengi


class Stage:
    
    # Set up the PyGame surface
    def __init__(self, caption, dimensions=None):
        
        # Try for 1024 x 768 like the original game otherwise pick highest resolution available
        # if dimensions == None:
        #     modes = pygame.display.list_modes()
        #     print(modes)
        #     if (1024, 768) in modes:
        #         dimensions = (1024, 768)
        #     else:
        #         dimensions = modes[0]
        dimensions = kengi.get_surface().get_size()

        # pygame.display.set_mode(dimensions, FULLSCREEN)
        pygame.mouse.set_visible(False)

        pygame.display.set_caption(caption)
        self.screen = kengi.get_surface()  #pygame.display.get_surface()
        self.spr_list = list()
        self.width = dimensions[0]
        self.height = dimensions[1]
        self.showBoundingBoxes = False

    @staticmethod
    def from_pts_list_to_bbox(plist):
        minx = float('inf')
        miny = float('inf')

        maxx = float('-inf')
        maxy = float('-inf')
        for p in plist:
            if p[0] < minx:
                minx = p[0]
            if p[0] > maxx:
                maxx = p[0]
            if p[1] < miny:
                miny = p[1]
            if p[1] > maxy:
                maxy = p[1]
        a,b,c,d =minx, miny, 1+(maxx-minx), 1+(maxy-miny)
        if a<0:
            c += a
            a = 0
        if b<0:
            d += b
            b = 0
        tmp = pygame.rect.Rect(a, b, c, d)
        #print('tmp---------->', tmp, type(tmp))
        return tmp

    # Add sprite to list then draw it as a easy way to get the bounding rect    
    def add_sprite(self, sprite):
        self.spr_list.append(sprite)

        pts_list = sprite.draw()
        #print('pts_list ', 'is', pts_list)
        # TODO fix pygemu, so we can use the org line:
        pygame.draw.lines(self.screen, sprite.color, True, pts_list, 2)  # .aalines
        #print('sprite.boundingRect printed out : ', test , '..\n')

        # - tom's hack
        sprite.boundingRect = Stage.from_pts_list_to_bbox(pts_list)
        # if test.width != sprite.boundingRect.width:
        #     raise Exception
        # if test.height != sprite.boundingRect.height:
        #     raise Exception

    def remove_sprite(self, sprite):
        self.spr_list.remove(sprite)
        
    def draw_sprites(self):
        for sprite in self.spr_list:

            pts_li = sprite.draw()
            pygame.draw.lines(self.screen, sprite.color, True, pts_li, 2)  # .aalines
            #update boundingRect
            sprite.boundingRect = Stage.from_pts_list_to_bbox(pts_li)

            #sprite.boundingRect = ..

            #if self.showBoundingBoxes:
            #    pygame.draw.rect(self.screen, (255, 255, 255), sprite.boundingRect, 1)

    def move_sprites(self):
        for sprite in self.spr_list:
            sprite.move()
     
            if sprite.position.x < 0:
                sprite.position.x = self.width
                
            if sprite.position.x > self.width:
                sprite.position.x = 0
            
            if sprite.position.y < 0:
                sprite.position.y = self.height
                
            if sprite.position.y > self.height:
                sprite.position.y = 0