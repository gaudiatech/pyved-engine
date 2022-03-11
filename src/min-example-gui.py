import katagames_engine as kengi

pygame = kengi.pygame
kengi.core.init()
screen = kengi.core.get_screen()
width, height = screen.get_size()
FT_PATH = 'alphbeta.ttf'
INIT_TXT = 'hello user this\nis\nsome\ndope\ntext'
ALT_TXT = 'i\nunderstand that\nyou watch the console'
block = kengi.gui.TextBlock(FT_PATH, 32, INIT_TXT, (0, 0, 0))
block.rect.center = (width // 2, height // 2)  # lets center the text block
print('*~*~*\npress and hold the space bar ; press ENTER to change alignment')
ended = False

while not ended:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            ended = True
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_RETURN:
                block.text_align = (block.text_align + 1) % 2  # switch text align
            elif ev.key == pygame.K_SPACE:
                block.text = ALT_TXT
        elif ev.type == pygame.KEYUP:
            if not pygame.key.get_pressed()[pygame.K_SPACE]:
                block.text = INIT_TXT
    screen.fill('white')
    block.draw(screen)
    kengi.core.display_update()
kengi.core.cleanup()
