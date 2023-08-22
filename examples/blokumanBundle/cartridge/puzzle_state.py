from . import glvars
from . import util
# alias
vars = glvars
from .puzzle_compo import PuzzleCtrl, PuzzleView, BoardModel, BagFulloPieces
from .ev_types import BlokuEvents


kengi = vars.katasdk.pyved_engine
pygame = kengi.pygame


class ScoreView(kengi.EvListener):
    """
    displays the score, play sounds
    """

    def __init__(self, boardmod, orgpoint, board_px_width):
        super().__init__()
        self.board_px_width = board_px_width

        self._board_model = boardmod
        self.score_img = None
        self.org_point = orgpoint

        self.font_color = glvars.colors['c_lightpurple']
        self.bgcolor = glvars.colors['c_purple']

        self.go_font = glvars.fonts['moderne_big']
        self.sc_font = glvars.fonts['sm_monopx']

        # sons
        # self.sfx_explo = pygame.mixer.Sound('assets/explo_basique.wav')
        self.sfx_crumble = kengi.vars.sounds['crumble']  # pygame.mixer.Sound('user_assets/blokuman-crumble.wav')

        # - labels
        self._gameover_img_bg = kengi.vars.images['blokuman-bt_rouge']  #pygame.image.load('user_assets/blokuman-bt_rouge.png')

        self._gameover_img_label = None

        self.flag_game_over = False

        self.scr = kengi.get_surface()
        self.view_width, self.view_height = self.scr.get_size()

        self.refresh_score_img(self._board_model.score)

    def refresh_score_img(self, num_val):
        self.score_img = self.sc_font.render("SCORE {:06d}".format(num_val), False, self.font_color)

    def on_event(self, ev):
        if ev.type == kengi.EngineEvTypes.Paint:
            self._paint(ev.screen)

        elif ev.type == BlokuEvents.ScoreChanges:
            self.refresh_score_img(ev.score)

        elif ev.type == BlokuEvents.LineDestroyed:
            util.playsfx(self.sfx_crumble)

    def _paint(self, screen):
        imgw, imgh = self.score_img.get_size()
        tx, ty = self.org_point[0] + (self.board_px_width - imgw) // 2, self.org_point[1] - imgh
        screen.blit(self.score_img, (tx, ty))

        if self.flag_game_over:
            self.draw_game_over_msg(screen)

    def draw_game_over_msg(self, ecran):
        # -- affiche simili -popup
        targetp = [self.view_width // 2, self.view_height // 2]
        targetp[0] -= self._gameover_img_bg.get_size()[0] // 2
        targetp[1] -= self._gameover_img_bg.get_size()[1] // 2
        ecran.blit(self._gameover_img_bg, targetp)

        # -- affiche msg
        if not self._gameover_img_label:
            self._gameover_img_label = self.go_font.render("Jeu termine, ENTREE pr sortir", False, self.font_color)

        r = self._gameover_img_label.get_rect()
        targetpos = (
            (self.view_width // 2) - (r.width // 2),
            (self.view_height // 2) - (r.height // 2)
        )
        ecran.blit(self._gameover_img_label, targetpos)


class PuzzleState(kengi.BaseGameState):
    """
    classe qui gère le mode de jeu
    ou l'on assemble des pièces en tetromino
    """

    def __init__(self, state_ident):
        super().__init__(state_ident)
        self._ctrl = None
        self.ma_vue = None
        self.score_view = None

    def enter(self):
        the_board = BoardModel(10, 10)  # un arg supplémentaire ne servirait a rien
        avail = BagFulloPieces(the_board)

        # -- - - we used to init seed -  - - -
        # damod.rand.seed(glvars.chall_seed)

        da_cfonts = {}
        if pygame.font.get_init():
            da_cfonts["game_over"] = pygame.font.Font(None, 60)  # Sysfont "ni7seg"
            da_cfonts["score"] = pygame.font.Font(None, 18)

        # - view creation
        pos_origine = (16, 40)
        self.ma_vue = PuzzleView(the_board, avail, pos_origine)
        self.score_view = ScoreView(the_board, pos_origine, self.ma_vue.px_width)

        self.ma_vue.turn_on()
        self.score_view.turn_on()

        # - ctrl
        self._ctrl = PuzzleCtrl(the_board, avail, self.ma_vue, self.score_view)

        # -launch
        self._ctrl.turn_on()

    def release(self):
        self._ctrl.turn_off()
        self.ma_vue.turn_off()
        self.score_view.turn_off()
