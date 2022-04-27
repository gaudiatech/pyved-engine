import pygame


# constants
BG_COLOR = 'antiquewhite2'
COLOR_PALETTE = {
    0: (244, 105, 251),
    1: (105, 184, 251)
}
SCR_SIZE = (480, 270)


class SharedVars:
    def __init__(self):
        self.game_over = False
        self.av_y_speed = 0
        self.curr_color_code = 0


def event_handling(ev_queue, state):
    for ev in ev_queue:
        if ev.type == pygame.QUIT:
            state.game_over = True

        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                state.game_over = True
            elif ev.key == pygame.K_SPACE:
                state.curr_color_code = (state.curr_color_code + 1) % 2
            elif ev.key == pygame.K_UP:
                state.av_y_speed = -1
            elif ev.key == pygame.K_DOWN:
                state.av_y_speed = 1

        elif ev.type == pygame.KEYUP:
            prkeys = pygame.key.get_pressed()
            if (not prkeys[pygame.K_UP]) and (not prkeys[pygame.K_DOWN]):
                state.av_y_speed = 0


def play_game():
    av_pos = [240, 135]
    game_st = SharedVars()
    screen = pygame.display.set_mode(SCR_SIZE)
    clock = pygame.time.Clock()

    while not game_st.game_over:
        event_handling(pygame.event.get(), game_st)

        av_pos[1] = (av_pos[1] + game_st.av_y_speed) % SCR_SIZE[1]

        screen.fill(BG_COLOR)
        pl_color = COLOR_PALETTE[game_st.curr_color_code]
        pygame.draw.circle(screen, pl_color, av_pos, 15, 0)
        pygame.display.update()
        clock.tick(60)


if __name__ == '__main__':
    print("Demo A | controls:")
    print("UP/DOWN arrow, SPACE, ESCAPE")
    pygame.init()
    pygame.display.set_caption('demo-a uses pygame only')
    play_game()
    pygame.quit()
    print('bye.')
