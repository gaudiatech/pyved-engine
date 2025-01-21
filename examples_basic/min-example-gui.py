import pyved_engine as pyv
pyv.init(2)

pygame = pyv.pygame
screen = pyv.get_surface()
width, height = screen.get_size()

INIT_TXT = 'hello user this\nis\nsome\ndope\ntext'
ALT_TXT = 'i\nunderstand that\nyou watch the console'
USING_IMGBASED_FT = True

if USING_IMGBASED_FT:
    ft_obj = pyv.gui.ImgBasedFont(
        (15, 130, 243),  # we specify: the color that should be viewed as transparent
        img=pygame.image.load('niobe_font.png')
    )  # special font format
else:
    FT_PATH = 'alphbeta.ttf'
    ft_obj = pygame.font.Font(FT_PATH, 16)


block = pyv.gui.TextBlock(ft_obj, INIT_TXT, (0, 0, 0))
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
    pyv.flip()
pyv.quit()
