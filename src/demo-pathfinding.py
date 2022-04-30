import katagames_engine as kengi

kengi.init('old_school', caption='demo-pathfinding uses kengi')
pygame = kengi.pygame

map_dim = (14, 9)
the_map = kengi.terrain.BoolMatrix(map_dim)
the_map.set_all(False)  # False means non-blocking

print(the_map)

# constants
BG_COLOR = 'antiquewhite2'
COLOR_PALETTE = {
    0: (144, 105, 151),
    1: (53, 25, 25)
}
START_DISP = (30, 30)
OFFSETS = (22, 22)

start_pos = [0, 0]
cursor_pos = [0, 0]
end_pos = list(map_dim)
end_pos[0] -= 1
end_pos[1] -= 1


def move_cursor(direct):
    global cursor_pos, map_dim
    if 'up' == direct:
        if cursor_pos[1] > 0:
            cursor_pos[1] -= 1
    elif 'down' == direct:
        if cursor_pos[1] < map_dim[1]-1:
            cursor_pos[1] += 1
    elif 'left' == direct:
        if cursor_pos[0] > 0:
            cursor_pos[0] -= 1
    elif 'right' == direct:
        if cursor_pos[0] < map_dim[0]-1:
            cursor_pos[0] += 1


class SharedVars:
    def __init__(self):
        self.game_over = False
        self.av_y_speed = 0
        self.curr_color_code = 0


last_res = None


def event_handling(ev_queue, state):
    global last_res
    for ev in ev_queue:
        if ev.type == pygame.QUIT:
            state.game_over = True

        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                state.game_over = True

            elif ev.key == pygame.K_BACKSPACE:
                last_res = None

            elif ev.key == pygame.K_RETURN:
                print('Pathfinding !')
                pathfinding_result = kengi.terrain.DijkstraPathfinder.find_path(
                    the_map, start_pos, end_pos
                )
                print(pathfinding_result)
                last_res = pathfinding_result

            elif ev.key == pygame.K_SPACE:
                i, j = cursor_pos
                if the_map.get_val(i, j):
                    the_map.set_val(i, j, False)
                    print('swap matrix value to false(non-blocking)')
                else:
                    the_map.set_val(i, j, True)
                    print('swap matrix value to True (blocking)')

            elif ev.key == pygame.K_UP:
                move_cursor('up')
            elif ev.key == pygame.K_DOWN:
                move_cursor('down')
            elif ev.key == pygame.K_LEFT:
                move_cursor('left')
            elif ev.key == pygame.K_RIGHT:
                move_cursor('right')

        elif ev.type == pygame.KEYUP:
            prkeys = pygame.key.get_pressed()
            if (not prkeys[pygame.K_UP]) and (not prkeys[pygame.K_DOWN]):
                state.av_y_speed = 0


def play_game():
    print('press RETURN to compute the path.')

    av_pos = [240, 135]
    game_st = SharedVars()
    screen = kengi.get_surface()
    scr_size = screen.get_size()
    clock = pygame.time.Clock()

    while not game_st.game_over:
        event_handling(pygame.event.get(), game_st)

        av_pos[1] = (av_pos[1] + game_st.av_y_speed) % scr_size[1]

        # - screen update
        screen.fill(BG_COLOR)

        for i in range(map_dim[0]):
            for j in range(map_dim[1]):

                pos = list(START_DISP)
                pos[0] += i * OFFSETS[0]
                pos[1] += j * OFFSETS[1]

                # pick a color based on if its blocking or not ; if it belongs to the path or not
                idx = 1 if the_map.get_val(i, j) else 0
                chosen_color = COLOR_PALETTE[idx]
                if last_res is not None:
                    if (i, j) in last_res:
                        chosen_color = 'orange'

                pygame.draw.circle(screen, chosen_color, pos, 10, 0)

        # show the cursor
        a, b = -10 + cursor_pos[0] * OFFSETS[0] + START_DISP[0], -10 + cursor_pos[1] * OFFSETS[1] + START_DISP[1]
        pygame.draw.rect(screen, 'navyblue', (a, b, 20, 20), 1)

        kengi.flip()
        clock.tick(60)


if __name__ == '__main__':
    print("KENGI pathfinding demo | Controls:")
    print()
    print('- ARROW keys')
    print('- SPACE to set blocking/non-blocking')
    print('- RETURN to compute path')
    print('- BACKSPACE to clear last result')

    play_game()
    kengi.quit()
    print('done.')
