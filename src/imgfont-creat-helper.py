import katagames_engine as kengi


kengi.init('old_school')
pygame = kengi.pygame
screen = kengi.get_surface()
width, height = screen.get_size()
FT_PATH = 'alphbeta.ttf'
pyg_font = pygame.font.Font(FT_PATH, 12)

block = kengi.gui.TextBlock(
    pyg_font, 'no text', (255, 0, 0)  # pick either pyg_font or custom_ft
)

block.rect.center = (width // 2, height // 2)  # lets center the text block
print('*~*~*\npress and hold the space bar ; press ENTER to change alignment')
can_exit = False

GL_BG_COLOR = (0, 0, 0)
block.debug = 0

# sert a afficher tous les car. sans exception!
INIT_TXT = "ABCDEFGHIJKLMNOPQRSTUVWXYZa\nabcdefghijklmnopqrstuvwxyz.\n"
INIT_TXT += ".-,:+\'!?0\n0123456789()/_=\\[]*\"<>;@$%{}'\n"
block.text = INIT_TXT

while not can_exit:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            can_exit = True
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_RETURN:
                block.text_align = (block.text_align + 1) % 2  # switch text align
        elif ev.type == pygame.KEYUP:
            if not pygame.key.get_pressed()[pygame.K_SPACE]:
                block.text = INIT_TXT
    screen.fill(GL_BG_COLOR)
    block.draw(screen)
    kengi.flip()

kengi.quit()
