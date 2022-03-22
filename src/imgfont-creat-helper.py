import katagames_engine as kengi
kengi.init()


pygame = kengi.pygame
screen = kengi.get_surface()
width, height = screen.get_size()
FT_PATH = 'alphbeta.ttf'

INIT_TXT = 'hello user this\nis\nsome\ndope\ntext'
ALT_TXT = 'i\nunderstand that\nyou watch the console'

pyg_font = pygame.font.Font(FT_PATH, 12)

#custom_ft = kengi.gui.ImgBasedFont('ma_font.png', (220,15,33) )

#print(custom_ft.letter_spacing)

block = kengi.gui.TextBlock(
    pyg_font, INIT_TXT, (255,0,0)  # pick either pyg_font or custom_ft
)

block.rect.center = (width // 2, height // 2)  # lets center the text block
print('*~*~*\npress and hold the space bar ; press ENTER to change alignment')
ended = False

GL_BG_COLOR = (0,0,0)

# - debug -
block.debug=0

# pr afficher tous les car!!
INIT_TXT = "ABCDEFGHIJKLMNOPQRSTUVWXYZa\nabcdefghijklmnopqrstuvwxyz.\n"
INIT_TXT += ".-,:+\'!?0\n0123456789()/_=\\[]*\"<>;'\n"
block.text = INIT_TXT

# tmp_ft_part = pygame.Surface((custom_ft.width('hello'), 52))
#tmp_ft_part.fill((255,255,255))
# custom_ft.render('hello', tmp_ft_part, (2,2))

# def render(self, text, surf, loc, line_width=0):
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
    screen.fill(GL_BG_COLOR)
    block.draw(screen)
    #screen.blit(tmp_ft_part, (32,168))
    #custom_ft.render('hello', screen, (2,2), 1)
    kengi.flip()
kengi.quit()
