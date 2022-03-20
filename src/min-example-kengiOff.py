import pygame
pygame.init()
scr_size = (480, 270)

avpos = [240, 135]
av_y_speed = 0
clock = pygame.time.Clock()
screen = pygame.display.set_mode(scr_size)
bgcolor = 'antiquewhite2'
print('\n[kengi demo]\nTRACKED KEYS: up/down arrow keys ; Spacebar ; Escape')
acolors = {
    0: (244, 105, 251),
    1: (105, 184, 251)
}
curr_color_code = 0
gameover = False

while not gameover:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            gameover = True
        elif ev.type == pygame.KEYUP:
            prkeys = pygame.key.get_pressed()
            if (not prkeys[pygame.K_UP]) and (not prkeys[pygame.K_DOWN]):
                av_y_speed = 0
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_UP:
                av_y_speed = -1
            elif ev.key == pygame.K_DOWN:
                av_y_speed = 1
            elif ev.key == pygame.K_SPACE:
              curr_color_code = (curr_color_code + 1) % 2
            elif ev.key == pygame.K_ESCAPE:
              gameover = True

    avpos[1] = (avpos[1] + av_y_speed) % scr_size[1]
    
    screen.fill(bgcolor)
    pygame.draw.circle(screen, acolors[curr_color_code], avpos, 15, 0)
    pygame.display.update()
    clock.tick(60)

pygame.quit()
print('game over.')
