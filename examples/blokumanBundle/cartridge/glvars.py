



#  GLOBAL VARS
# ----------------------
katasdk = None
util = None

username = None
acc_id = None

# specific
solde_gp = None
border_fade_colour = None
colour_map = None
song = None
snd_channels = dict()
num_lastchannel = 0  # pr alterner entre 0 et 1
copie_solde = None
colors = dict()
fonts = dict()
num_challenge = None  # sera un entier
chall_seed = 1  # sera un entier déterminant cmt générateur aléatoire va sortir les données du problème d'optim.
multiplayer_mode = None  # sera déterminé en fct de s'il y a des joueurs "remote"
server_host = None  # recevra un str
server_port = None  # recevra un int
server_debug = None

# ----------------------
#  CONSTANTS
# ----------------------
DEV_MODE = True
GAME_ID = 8  # 8 pour blokuman, c codé en dur coté serv
SKIP_MINING = False
SQ_SIZE = 20
BORDER_SIZE = 3
MAX_FPS = 45
VERSION = '0.20.1a'
RESSOURCE_LOC = ['assets']
CHOSEN_LANG = 'fr'
# codes
NOP, CHOIX_LOGIN, CHOIX_START, CHOIX_CRED, CHOIX_QUIT = range(5)