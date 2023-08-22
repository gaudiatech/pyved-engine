
from . import glvars
from .TetColors import TetColors

# ----------------------
#  UTIL. FUNCTIONS
# ----------------------
# def cli_logout():
#     global nom_utilisateur, solde_gp, id_perso
#     nom_utilisateur = solde_gp = id_perso = None


def load_server_config():
    import os
    f = open(os.path.join('server.cfg'))

    config_externe = f.readlines()
    global server_host, server_port, server_debug
    k = int(config_externe[0])
    server_debug = False if (k == 0) else True
    server_host = config_externe[1].strip("\n")
    server_port = int(config_externe[2])


def init_sound():
    pyg = glvars.katasdk.pyved_engine.pygame
    if len(glvars.snd_channels) < 1:
        capital_n = 3
        pyg.mixer.set_num_channels(capital_n)
        for k in range(capital_n):
            glvars.snd_channels[k] = pyg.mixer.Channel(k)


def is_sfx_playin():
    for cn in range(2):
        if glvars.snd_channels[cn].get_busy():
            return True

    return False


def playmusic():
    pass
    # global snd_channels, song
    #
    # if not katasdk.runs_in_web():
    #
    #     if song is None:
    #         pygame.mixer.music.load('user_assets/chiptronic.ogg')
    #         song = 1
    #     pygame.mixer.music.play(-1)


def playsfx(pygamesound):
    # ToDO temp fix for webctx
    # global snd_channels, num_lastchannel
    # if not katasdk.runs_in_web():
    #     num_lastchannel = (num_lastchannel + 1) % 2
    #     snd_channels[num_lastchannel].play(pygamesound)
    pygamesound.play()


def init_fonts_n_colors():
    from .fonts_n_colors import my_fonts, my_colors
    import os

    # global border_fade_colour, colour_map, colors, fonts
    pyg = glvars.katasdk.pyved_engine.pygame
    border_fade_colour = pyg.Color(50, 50, 50)

    # - BLOc standardisé -
    pyg.font.init()
    for name, v in my_colors.items():
        glvars.colors[name] = pyg.Color(v)
    ressource_loc_li = ['.']
    for name, t in my_fonts.items():
        if t[0] is not None:
            tmp = list(ressource_loc_li)
            tmp.append(t[0])
            source = os.path.join(*tmp)
        else:
            source = None
        glvars.fonts[name] = pyg.font.Font(source, t[1])
    print('chargement fonts_n_colors *** OK!')

    # pygame.font.init()
    # for name, v in my_colors.items():
    #     colors[name] = pygame.Color(v)
    # for name, t in my_fonts.items():
    #     tmp = list(RESSOURCE_LOC)
    #     tmp.append(t[0])
    #     source = os.path.join(*tmp)
    #     fonts[name] = pygame.font.Font(source, t[1])

    # bonus algo, helper pour afficher tetromino sprites...
    glvars.colour_map = {
        TetColors.Gray: glvars.colors['c_gray2'],
        TetColors.Clear: glvars.colors['bgspe_color'],  #colors['c_lightpurple'],
        TetColors.Pink: glvars.colors['c_skin']
    }
