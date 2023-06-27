import pyved_engine as pyv


# constants
BG_COLOR = 'antiquewhite2'
COLOR_PALETTE = {
    0: (244, 105, 251),
    1: (105, 184, 251)
}


class SharedVars:
    def __init__(self):
        self.game_over = False
        self.av_y_speed = 0
        self.curr_color_code = 0


def event_handling(ev_queue, state):
    pygame = pyv.pygame
    for ev in ev_queue:
        if ev.type == pygame.QUIT:
            state.game_over = True

        elif ev.type == pyv.pygame.KEYDOWN:
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
    # -------------------
    #  demo STyle 1
    # -------------------
    pyv.init(2, caption='demo-a uses kengi / straightforward variant')

    av_pos = [240, 135]
    game_st = SharedVars()
    screen = pyv.get_surface()
    scr_size = screen.get_size()
    clock = pyv.vars.game_ticker  # pre-defined Clock in the pyved_engine!!

    while not game_st.game_over:  # <----- my own game loop

        event_handling(pyv.pygame.event.get(), game_st)
        av_pos[1] = (av_pos[1] + game_st.av_y_speed) % scr_size[1]
        screen.fill(BG_COLOR)
        pl_color = COLOR_PALETTE[game_st.curr_color_code]
        pyv.draw_circle(screen, pl_color, av_pos, 15, 0)
        pyv.flip()
        clock.tick(60)


"""
Right now (June 2023), there are 3 ways to define your game:

 1/ use any event system you like(the new one, or pygame legacy event system) + define your own game loop
 2/ use the new event system + objects from Pyv that can post/subscribe to events
 3/ use the pyv.GameTpl and redefine the .get_video_mode() method
"""

if __name__ == '__main__':
    print(" Pyved_engine straightforward variant of ~~~ Demo A | controls:")
    print("UP/DOWN arrow, SPACE, ESCAPE")
    play_game()
    pyv.close_game()
    print('bye.')
