import time

from . import serv_func as katapi
from .. import ext_gui as gui
from ..engine import BaseGameState
from ..engine import CogObject, EngineEvTypes, EventReceiver, EventManager, import_pygame, CgmEvent, runs_in_web
from ..engine.foundation import conf_eng as cgmconf


pygame = import_pygame()


class KataFrameM(CogObject):
    """
    classe utilisée pr stocker temporairement login / pwd
    durant le processus de login
    Le pwd est gardé secret (pas d'affichage) mais on compte et
    on affiche correctement le nb de car
    """
    VAR_USERNAME, VAR_PWD = range(87, 87 + 2)

    def __init__(self):
        super().__init__()
        self._username_info = ''
        self._pwdplain_info = ''

        self._focusing_username = True

    def input_char(self, c):
        if self._focusing_username:
            self._username_info += c
        else:
            self._pwdplain_info += c

    # - getters
    @property
    def username(self):
        return self._username_info

    @property
    def plainpwd(self):
        return self._pwdplain_info

    def get_pwd_str(self):
        k = len(self._pwdplain_info)
        li_etoiles = '*' * k
        return ''.join(li_etoiles)

    def is_focusing_username(self):
        return self._focusing_username

    # - misc methods
    def set_focus(self, var_code):

        if var_code == self.VAR_USERNAME:
            if not self._focusing_username:
                self._focusing_username = True
                self.pev(EngineEvTypes.FOCUSCH, focusing_username=True)

        elif var_code == self.VAR_PWD:
            if self._focusing_username:
                self._focusing_username = False
                self.pev(EngineEvTypes.FOCUSCH, focusing_username=False)
        else:
            raise ValueError('unrecognized var_code')

    def toggle_focus(self):
        self._focusing_username = not self._focusing_username
        self.pev(EngineEvTypes.FOCUSCH, focusing_username=self._focusing_username)

    def suppr_lettre(self):
        if self._focusing_username:
            if len(self._username_info) > 0:
                self._username_info = self._username_info[:-1]
                self.pev(EngineEvTypes.FIELDCH, field=0, txt=self._username_info)
        else:
            if len(self._pwdplain_info) > 0:
                self._pwdplain_info = self._pwdplain_info[:-1]
                self.pev(EngineEvTypes.FIELDCH, field=1, txt=self.get_pwd_str())

    def reset_fields(self):
        self._username_info = ''
        self._pwdplain_info = ''

        self.pev(EngineEvTypes.FIELDCH, field=0, txt=self._username_info)
        self.pev(EngineEvTypes.FIELDCH, field=1, txt=self.get_pwd_str())

        self._focusing_username = True
        self.pev(EngineEvTypes.FOCUSCH, focusing_username=True)


BIOS_FG_COL_DESC = 'purple'
BIOS_BG_COL_DESC = 'antiquewhite3'


class KataFrameV(EventReceiver):
    """
    affiche écran intermédiaire permettant la SAISIE des IDENT.
    """

    TEXT_INPUT_SIZE = 160
    ERR_MSG_DELAY = 2.5  # sec
    POS_BT_BROWSER = (385/2, 215/2)
    TAQ_XALIGN_BOX = 150
    TAQ_XALIGN_LABELS = 50
    VOFFSET = 24
    POS_BT_CONFIRM = (TAQ_XALIGN_LABELS, 199)
    POS_BT_CANCEL = (TAQ_XALIGN_LABELS, 199+30)

    # ------------------
    #  positions des labels
    # TODO ramener depuis extérieur classe

    def __init__(self, ref_mod):
        super().__init__()
        fgcolor, bgcolor = pygame.color.Color(BIOS_FG_COL_DESC), pygame.color.Color(BIOS_BG_COL_DESC)

        self.bgcolor = bgcolor
        self.fgcolor = fgcolor

        self._ref_mod = ref_mod

        self._font = pygame.font.Font(None, 22)
        self._buttons = list()
        self._crea_boutons()

        # self.red_color = glvars.colors['c_cherokee']
        self._fin_aff_flottant = None

        gui.Etiquette.set_font(self._font)

        init_yv = 22
        y_lig1 = init_yv+4*self.VOFFSET
        y_lig2 = init_yv+5*self.VOFFSET
        self._etiquettes = [
            gui.Etiquette('KATA.GAMES auth procedure', (self.TAQ_XALIGN_LABELS, init_yv), self.fgcolor),
            gui.Etiquette('if you need a new account, please', (self.TAQ_XALIGN_LABELS, init_yv+1*self.VOFFSET), self.fgcolor),
            gui.Etiquette('use our website https://kata.games', (self.TAQ_XALIGN_LABELS, init_yv+2*self.VOFFSET), self.fgcolor),
            gui.Etiquette('username', (self.TAQ_XALIGN_LABELS, y_lig1), self.fgcolor),
            gui.Etiquette('password', (self.TAQ_XALIGN_LABELS, y_lig2), self.fgcolor)
        ]

        self._err_etiquette = gui.Etiquette(
            'ERR: server does not recognize this account', (self.TAQ_XALIGN_LABELS, init_yv+3*self.VOFFSET), (255, 0, 0)
        )
        self.saisie_txt1 = gui.TextInput('>', self._font, KataFrameV.nop, (self.TAQ_XALIGN_BOX, y_lig1), self.TEXT_INPUT_SIZE)
        self.saisie_txt2 = gui.TextInput('>', self._font, KataFrameV.nop, (self.TAQ_XALIGN_BOX, y_lig2), self.TEXT_INPUT_SIZE)
        self.saisie_txt2.pwd_field = True

    @staticmethod
    def confirm_routine():
        # TODO déclencher interrogation serveur
        # TODO exporter trucs vers le contrôleur, c'est lui qui va popstate
        ev = CgmEvent(EngineEvTypes.DOAUTH)
        EventManager.instance().post(ev)

    @staticmethod
    def cancel_routine():
        ev = CgmEvent(EngineEvTypes.POPSTATE)  # state_ident=GameStates.IntroJeu)
        EventManager.instance().post(ev)

    @staticmethod
    def nop(txt):
        pass

    def _crea_boutons(self):
        txt = 'connection'
        bt = gui.Button2(self._font, txt, self.POS_BT_CONFIRM, KataFrameV.confirm_routine)
        self._buttons.append(bt)

        txt = 'abort'
        bt = gui.Button2(self._font, txt, self.POS_BT_CANCEL, KataFrameV.cancel_routine)
        self._buttons.append(bt)

    # - activation / désactivation impacte boutons également
    def turn_on(self, prio=None):
        super().turn_on()

        for bt in self._buttons:
            bt.turn_on()

        if self._ref_mod.is_focusing_username():
            self.saisie_txt1.focus()
            self.saisie_txt1.turn_on()
        else:
            self.saisie_txt2.focus()
            self.saisie_txt2.turn_on()

    def turn_off(self):
        super().turn_off()

        for bt in self._buttons:
            bt.turn_off()

        if self._ref_mod.is_focusing_username():
            self.saisie_txt1.no_focus()
            self.saisie_txt1.turn_off()
        else:
            self.saisie_txt2.no_focus()
            self.saisie_txt2.turn_off()

    # ########################################################
    #  proc_event
    # ########################################################
    def proc_event(self, ev, source):
        if ev.type == EngineEvTypes.PAINT:
            self._paint(ev.screen)

        # GUI controls
        elif ev.type == pygame.MOUSEBUTTONDOWN:
            if self.saisie_txt1.contains(ev.pos):
                self._ref_mod.set_focus(KataFrameM.VAR_USERNAME)
            elif self.saisie_txt2.contains(ev.pos):
                self._ref_mod.set_focus(KataFrameM.VAR_PWD)

        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_TAB:
                self._ref_mod.toggle_focus()
            elif ev.key == pygame.K_RETURN or ev.key == pygame.K_KP_ENTER:
                KataFrameV.confirm_routine()  # view > ctrl comm.

        # updating view (mod > view comm.)
        elif ev.type == EngineEvTypes.FIELDCH:
            if ev.field:  # pwd
                if ev.txt == '':
                    self.saisie_txt2.move_caret('home')
                    while self.saisie_txt2.get_disp_text() != '':
                        self.saisie_txt2.delete_char()
                    self.saisie_txt2.render_field()
            else:
                if ev.txt == '':
                    self.saisie_txt1.move_caret('home')
                    while self.saisie_txt1.get_disp_text() != '':
                        self.saisie_txt1.delete_char()
                    self.saisie_txt1.render_field()

        elif ev.type == EngineEvTypes.FOCUSCH:
            if ev.focusing_username:
                self._gui_focus_username()
            else:
                self._gui_focus_pwd()

    # - métier
    def _gui_focus_username(self):
        if self.saisie_txt2.has_focus():
            self.saisie_txt2.no_focus()
            self.saisie_txt2.turn_off()

            self.saisie_txt1.focus()
            self.saisie_txt1.turn_on()

    def _gui_focus_pwd(self):
        if self.saisie_txt1.has_focus():
            self.saisie_txt1.no_focus()
            self.saisie_txt1.turn_off()

            self.saisie_txt2.focus()
            self.saisie_txt2.turn_on()

    def _paint(self, screen):
        screen.fill(self.bgcolor)
        for e in self._etiquettes:
            screen.blit(e.img, e.pos)

        # - dessin boutons & widgets
        for b in self._buttons:
            screen.blit(b.image, b.position)
        screen.blit(self.saisie_txt1.image, self.saisie_txt1.position)
        screen.blit(self.saisie_txt2.image, self.saisie_txt2.position)

        if self._fin_aff_flottant is not None:
            t = time.time()
            if t > self._fin_aff_flottant:
                self._fin_aff_flottant = None
            else:
                screen.blit(self._err_etiquette.img, self._err_etiquette.pos)

    def sig_bad_auth(self):  # triggered externally by a ctrl class
        self._fin_aff_flottant = time.time() + self.ERR_MSG_DELAY


class KataFrameC(EventReceiver):

    def __init__(self, ref_mod, ref_view, storage_module):
        super().__init__()
        self.ref_mod = ref_mod
        self.ref_view = ref_view
        self.glvars_module = storage_module

    def proc_event(self, ev, source):
        if ev.type == EngineEvTypes.DOAUTH:
            self._handle_auth()

        elif ev.type == pygame.KEYDOWN:
            self._handle_keypress(ev)

        elif ev.type == pygame.QUIT:
            self.pev(EngineEvTypes.POPSTATE)

    def _handle_auth(self):
        login_feedback = katapi.try_auth_server(self.ref_mod.username, self.ref_mod.plainpwd)

        if login_feedback:
            username, acc_id = self.ref_mod.username, int(login_feedback)
            self.glvars_module.username = username
            self.glvars_module.acc_id = acc_id

            if runs_in_web():
                print('commit to session_storage ->ye')
                katapi.save_to_local_session(username, acc_id)
            self.pev(EngineEvTypes.CHANGESTATE, state_ident=0)

        else:
            self.ref_mod.reset_fields()
            # gestion refus -> affiche un message erreur
            self.ref_view.sig_bad_auth()

    def _handle_keypress(self, ev):
        if ev.key == pygame.K_RETURN or ev.key == pygame.K_KP_ENTER:
            pass

        elif ev.key == pygame.K_ESCAPE:
            self.pev(EngineEvTypes.POPSTATE)

        elif ev.key == pygame.K_TAB:
            return  # sert à ignorer caractères TAB ds la saisie

        elif ev.key == pygame.K_BACKSPACE:
            self.ref_mod.suppr_lettre()

        else:
            self.ref_mod.input_char(ev.unicode)  # register the key


class MicroView(EventReceiver):
    def __init__(self):
        super().__init__()
        fgcolor, self.bgcolor = pygame.color.Color('purple'), pygame.color.Color('antiquewhite3')

        self._font = pygame.font.Font(None, 22)

        self._label = self._font.render('CLICK HERE TO PLAY!', False, fgcolor)
        scr_w, scr_h = cgmconf.get_screen().get_size()
        self._pos = (
            (scr_w - self._label.get_width())//2,
            (scr_h - self._label.get_height())//2
        )

    def proc_event(self, ev, source):
        if ev.type == EngineEvTypes.PAINT:
            ev.screen.fill(self.bgcolor)
            ev.screen.blit(self._label, self._pos)

        elif ev.type == pygame.MOUSEBUTTONUP:
            self.pev(EngineEvTypes.CHANGESTATE, state_ident=0)


class KataFrameState(BaseGameState):

    def __init__(self, gs_ident, name, storage_module):
        super().__init__(gs_ident, name)
        self.m = self.v = self.c = None
        self.v2 = None
        self.glvars_module = storage_module

    def enter(self):
        print('BIOS in')
        self.m = KataFrameM()

        # the state can change right away, if login info is found...
        if not katapi.has_pre_auth():
            self.v = KataFrameV(self.m)
        else:
            username, player_id = katapi.get_credentials()
            print('fetched from session storage: {}, {}'.format(username, player_id))
            self.glvars_module.username = username
            self.glvars_module.acc_id = player_id
            self.v = MicroView()

        self.c = KataFrameC(self.m, self.v, self.glvars_module)
        self.c.glvars_module = self.glvars_module

        self.resume()

    def release(self):
        print('BIOS out')
        self.pause()
        self.m = self.v = self.c = None

    def pause(self):
        if self.v:
            self.v.turn_off()
        else:
            self.v2.turn_off()
        self.c.turn_off()

    def resume(self):
        self.v.turn_on()
        self.c.turn_on()
