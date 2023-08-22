import random

from . import glvars
from . import util
from .ev_types import BlokuEvents
from .labels import Labels
from .loctexts import tsl


kengi = glvars.katasdk.pyved_engine
pygame = kengi.pygame


class TitleView(kengi.EvListener):
    """
    se basera sur un modèle pouvant alterner entre DEUX etats:
    (1) guest, et (2) player_known
    le choix "start" ne sera dévérouillé que dans le cas 2
    """

    TXT_COLOR_HL = (217, 25, 84)
    TXT_COLOR = (110, 80, 90)

    POS_ETQ_VER = None

    REAL_TITLE = '- BLoKu Man -'
    BROKEN_TIT = '+ bL0Ku m4N ~'

    FG_COLOR = glvars.colors['c_lightpurple']
    TITLE_COLOR = glvars.colors['c_mud']
    BG_COLOR = glvars.colors['bgspe_color']
    SELEC_COLOR = glvars.colors['c_oceanblue']

    def __init__(self, ref_mod):
        super().__init__()
        self._pos_labels = dict()

        self.scr_size = kengi.get_surface().get_size()
        self.midx = self.scr_size[0]//2

        # - retro effect, part 1
        # self._vscr_size = (SCR_W, SCR_H)
        # self._vscreen = pygame.Surface(self._vscr_size)

        # - son
        self.sfx_low = kengi.vars.sounds['coinlow']  # pygame.mixer.Sound('user_assets/coinlow.wav')
        self.sfx_high = kengi.vars.sounds['coinhigh']  # pygame.mixer.Sound('user_assets/coinhigh.wav')

        # - polices de car.
        self._bigfont = glvars.fonts['moderne_big']
        self._medfont = glvars.fonts['moderne']

        # ****************** creation etiquettes pr le menu ******************
        self._options_menu = {
            glvars.CHOIX_LOGIN: 'Start game',
            glvars.CHOIX_START: 'Demarrer defi',
            glvars.CHOIX_CRED: '?? Unavaible yet',
            glvars.CHOIX_QUIT: 'Exit game'
        }
        # # TODO clean up
        # if kataen.runs_in_web():
        #     self._options_menu[TitleModel.CHOIX_QUIT] = 'Log out'

        self._options_labels = dict()
        for code in self._options_menu.keys():
            self._reset_label_option(code)

        self._mem_option_active = None
        self.activation_option(ref_mod.get_curr_choice())

        # ****************** prepa pour effets particules ******************
        # self._allwalker_pos = list()
        # self._walker_speed = dict()
        #
        # for k in range(20):
        #     self._walker_speed[k] = random.randint(1, 6)
        #
        #     i, j = random.randint(0, self.scr_size[0] - 1), random.randint(0, self.scr_size[1] - 1)
        #     self._allwalker_pos.append([i, j])

        self._label_titre = self._bigfont.render(
            self.REAL_TITLE, False, self.TITLE_COLOR
        )
        self._pos_titre = (
            (self.scr_size[0] - self._label_titre.get_size()[0]) // 2,
            50
        )

        self.mod = ref_mod
        self._hugefont = glvars.fonts['moderne']
        spefont = glvars.fonts['tiny_monopx']
        self._font = glvars.fonts['tiny_monopx']
        self._smallfont = glvars.fonts['tiny_monopx']
        self._boutons = list()
        self.bt_chall = None
        self.bt_login = None
        self.bt_exit = None

        # - crea etiquettes qui habillent bouton challenge
        kengi.gui.Etiquette.set_font(glvars.fonts['moderne'])
        self._etq_user = None
        self._etq_solde = None
        self.refresh_graphic_state()

    @staticmethod
    def prettify(txt):
        return '/\\----[__' + txt + '__]----\\/'

    def _reset_label_option(self, code):
        txt = self._options_menu[code]
        adhoc_label = self._medfont.render(txt, False, self.FG_COLOR)
        self._options_labels[code] = adhoc_label

    def activation_option(self, code):
        if self._mem_option_active is not None:
            util.playsfx(self.sfx_low)
            self._reset_label_option(self._mem_option_active)

        tmp = self._options_menu[code]
        txt = TitleView.prettify(tmp)
        adhoc_label = self._medfont.render(txt, False, self.SELEC_COLOR)
        self._options_labels[code] = adhoc_label

        self._mem_option_active = code

    def validate_effect(self):
        util.playsfx(self.sfx_high)

    def refresh_graphic_state(self):
        label_user = tsl(Labels.Utilisateur)
        label_solde = tsl(Labels.Solde)
        spe_color = (210, 33, 35)
        self._etq_user = self._medfont.render(
            '{}= {}'.format(label_user, self.mod.get_username()), False, spe_color
        )
        if self.mod.is_logged():
            self._etq_solde = self._medfont.render(
                '{}= {} MOBI'.format(label_solde, self.mod.get_solde()), False, spe_color
            )
        else:
            self._etq_solde = None

    def on_event(self, ev):
        if ev.type == kengi.EngineEvTypes.Paint:
            self._paint(ev.screen)

        elif ev.type == kengi.EngineEvTypes.Mousemotion:
            mx, my = kengi.proj_to_vscreen(ev.pos)
            for cod, lbl in self._options_labels.items():
                if cod in self._pos_labels:
                    ix, iy = self._pos_labels[cod]
                    w, h = lbl.get_size()
                    if ix < mx < ix+w:
                        if iy < my < iy+h:
                            if self.mod.get_curr_choice()!= cod:
                                self.mod.set_choice(cod)

        elif ev.type == kengi.EngineEvTypes.Mousedown:
            self.validate_effect()
            self.pev(BlokuEvents.Validation)

        elif ev.type == BlokuEvents.ChoiceChanges:
            self.activation_option(ev.code)

        elif ev.type == BlokuEvents.BalanceChanges:
            self.refresh_graphic_state()

    def dessin_boutons(self, screen):
        base_y = 128
        base_x = self.midx
        offset = 0
        if glvars.username:
            omega_choix = (glvars.CHOIX_START, glvars.CHOIX_CRED, glvars.CHOIX_QUIT)
        else:
            omega_choix = (glvars.CHOIX_LOGIN, glvars.CHOIX_CRED, glvars.CHOIX_QUIT)

        for c in omega_choix:
            label = self._options_labels[c]
            pos = (base_x - (label.get_size()[0] // 2), base_y + offset)
            offset += 40
            self._pos_labels[c] = list(pos)
            screen.blit(label, self._pos_labels[c])

    def _paint(self, screen):
        screen.fill(self.BG_COLOR)

        # - dessin bonhommes
        # for k, pos in enumerate(self._allwalker_pos):
        #     spd = self._walker_speed[k]
        #     pos[1] += spd
        #     if spd in (1, 2):
        #         spd_based_color = glvars.colors['c_mud']
        #     elif spd in (3, 4):
        #         spd_based_color = glvars.colors['c_brown']
        #     else:
        #         spd_based_color = glvars.colors['c_gray1']
        #
        #     pos[1] = pos[1] % self.scr_size[1]
        #     pygame.draw.rect(screen, spd_based_color, (pos[0], pos[1], 4, 6))

        # - dessin titre
        if random.random() < 0.1:
            if random.random() > 0.8:
                txt = self.REAL_TITLE
            else:
                txt = self.BROKEN_TIT
            self._label_titre = self._bigfont.render(txt, False, self.TITLE_COLOR)

        screen.blit(self._label_titre, self._pos_titre)

        # -- menu --
        self.dessin_boutons(screen)

        if self._etq_solde:
            screen.blit(self._etq_user, (int(0.05*self.scr_size[0]), 6))
            screen.blit(self._etq_solde, (int(0.05*self.scr_size[0]), 26))
        # - retro effect part 2
        # pygame.transform.scale(screen, glvars.SCREEN_SIZE, screen)

    # association état avec ceux des boutons
    def turn_on(self, prio=None):
        super().turn_on()
        for bt in self._boutons:
            bt.turn_on()
        self.refresh_graphic_state()

    def turn_off(self):
        super().turn_off()
        for bt in self._boutons:
            bt.turn_off()
