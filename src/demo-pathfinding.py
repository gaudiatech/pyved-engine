import katagames_engine as kengi

kengi.init('old_school', caption='demo-pathfinding uses kengi')
pygame = kengi.pygame


# constants
MAP_DIM = (14, 9)
BG_COLOR = 'antiquewhite2'
COLOR_PALETTE = {
    0: (144, 105, 151),
    1: (53, 25, 25)
}
START_DISP = (30, 30)
OFFSETS = (22, 22)
MAXFPS = 60
DEBUG_MSG = '** computing path **'


# global variables
demo_instructions = [
    '||KENGI pathfinding demo||',
    'Controls: ',
    '- ARROW keys',
    '- SPACE to set blocking/non-blocking',
    '- BACKSPACE to clear last computed result',
    'Most important: ',
    '- when RETURN is pressed the shortest path between {} and {} is computed',
]
start_pos = [0, 0]
cursor_pos = [0, 0]
end_pos = list(MAP_DIM)
end_pos[0] -= 1
end_pos[1] -= 1
demo_instructions[-1] = demo_instructions[-1].format(start_pos, end_pos)
the_map = kengi.terrain.BoolMatrix(MAP_DIM)
the_map.set_all(False)  # False means non-blocking
print(the_map)


class SharedVars:
    def __init__(self):
        self.game_over = False
        self.curr_color_code = 0
        self.last_res = None


def move_cursor(direct):
    global cursor_pos, MAP_DIM
    if 'up' == direct:
        if cursor_pos[1] > 0:
            cursor_pos[1] -= 1
    elif 'down' == direct:
        if cursor_pos[1] < MAP_DIM[1]-1:
            cursor_pos[1] += 1
    elif 'left' == direct:
        if cursor_pos[0] > 0:
            cursor_pos[0] -= 1
    elif 'right' == direct:
        if cursor_pos[0] < MAP_DIM[0]-1:
            cursor_pos[0] += 1


def event_handling(ev_queue, state):
    for ev in ev_queue:
        if ev.type == pygame.QUIT:
            state.game_over = True

        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                state.game_over = True

            elif ev.key == pygame.K_BACKSPACE:
                state.last_res = None

            elif ev.key == pygame.K_RETURN:
                print(DEBUG_MSG)
                pathfinding_result = kengi.terrain.DijkstraPathfinder.find_path(
                    the_map, start_pos, end_pos
                )
                print(pathfinding_result)
                state.last_res = pathfinding_result

            elif ev.key == pygame.K_SPACE:
                i, j = cursor_pos
                if the_map.get_val(i, j):
                    the_map.set_val(i, j, False)
                else:
                    the_map.set_val(i, j, True)

            elif ev.key == pygame.K_UP:
                move_cursor('up')
            elif ev.key == pygame.K_DOWN:
                move_cursor('down')
            elif ev.key == pygame.K_LEFT:
                move_cursor('left')
            elif ev.key == pygame.K_RIGHT:
                move_cursor('right')


def play_game():
    game_st = SharedVars()
    screen = kengi.get_surface()
    clock = pygame.time.Clock()

    while not game_st.game_over:
        event_handling(pygame.event.get(), game_st)

        # - screen update
        screen.fill(BG_COLOR)

        for i in range(MAP_DIM[0]):
            for j in range(MAP_DIM[1]):

                pos = list(START_DISP)
                pos[0] += i * OFFSETS[0]
                pos[1] += j * OFFSETS[1]

                # pick a color based on if its blocking or not ; if it belongs to the path or not
                idx = 1 if the_map.get_val(i, j) else 0
                chosen_color = COLOR_PALETTE[idx]
                if game_st.last_res is not None:
                    if (i, j) in game_st.last_res:
                        chosen_color = 'orange'

                pygame.draw.circle(screen, chosen_color, pos, 10, 0)

        # show the cursor
        a, b = -10 + cursor_pos[0] * OFFSETS[0] + START_DISP[0], -10 + cursor_pos[1] * OFFSETS[1] + START_DISP[1]
        pygame.draw.rect(screen, 'navyblue', (a, b, 20, 20), 1)

        kengi.flip()
        clock.tick(MAXFPS)


if __name__ == '__main__':
    for line in demo_instructions:
        print(line)
    play_game()
    kengi.quit()
    print('done.')
