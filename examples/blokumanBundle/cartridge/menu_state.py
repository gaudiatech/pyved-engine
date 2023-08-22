from . import defs
from . import glvars
from . import util
from .TitleView import TitleView
from .ev_types import BlokuEvents
from .labels import Labels
from .loctexts import tsl


pyv = glvars.katasdk.pyved_engine
pygame = pyv.pygame
EngineEvTypes = pyv.EngineEvTypes


class TitleModel(pyv.Emitter):
    """
    stocke l'info. si le joueur est connecté ou nom
    """
    COUT_PARTIE = 10

    def __init__(self):
        super().__init__()
        self.is_real_login = True
        self._curr_choice = glvars.CHOIX_LOGIN
        self._logged_in = False

    def reset(self):
        self._logged_in = False

    def reset_choice(self):
        if self.is_logged():
            self._curr_choice = glvars.CHOIX_START
        else:
            self._curr_choice = glvars.CHOIX_LOGIN
        self.pev(BlokuEvents.ChoiceChanges, code=self._curr_choice)

    def get_curr_choice(self):
        return self._curr_choice

    def set_choice(self, val):
        self._curr_choice = val
        self.pev(BlokuEvents.ChoiceChanges, code=self._curr_choice)

    def move(self, direction):
        assert direction in (-1, +1)
        self._curr_choice += direction

        if not self.is_logged():
            if self._curr_choice == glvars.CHOIX_START:
                self._curr_choice += direction
            if self._curr_choice > glvars.CHOIX_QUIT:
                self._curr_choice = glvars.CHOIX_LOGIN
            elif self._curr_choice < glvars.CHOIX_LOGIN:
                self._curr_choice = glvars.CHOIX_QUIT

            self.pev(BlokuEvents.ChoiceChanges, code=self._curr_choice)
            return

        # on est connecté
        if self._curr_choice == glvars.CHOIX_LOGIN:
            self._curr_choice += direction
        if self._curr_choice > glvars.CHOIX_QUIT:
            self._curr_choice = glvars.CHOIX_START
        elif self._curr_choice < glvars.CHOIX_START:
            self._curr_choice = glvars.CHOIX_QUIT
        self.pev(BlokuEvents.ChoiceChanges, code=glvars._curr_choice)

    # def force_fakelogin(self):
    #     glvars.solde_gp = 10
    #     glvars.username = 'ghost'
    #     kevent.EventManager.instance().post(
    #         kevent.CgmEvent(BlokuEvents.BalanceChanges, value=10)
    #     )
    #     self.is_real_login = False

    def is_logged(self):
        return glvars.username is not None

    def mark_auth_done(self, solde_gp):
        self._logged_in = True
        glvars.solde_gp = solde_gp

    def can_bet(self):
        if not self._logged_in:
            return False
        if self.get_solde() is None:
            return False
        return self.get_solde() >= self.COUT_PARTIE

    def get_username(self):
        if not self.is_logged():
            return tsl(Labels.NomJoueurAnonyme)
        return glvars.username

    def set_solde(self, val):
        glvars.solde_gp = val
        pyv.get_ev_manager().post(
            BlokuEvents.BalanceChanges, value=val
        )

    def get_solde(self):
        if not self.is_logged():
            raise Exception('demande solde alors que _logged_in à False')
        return glvars.solde_gp


class MenuCtrl(pyv.EvListener):
    POLLING_FREQ = 4  # sec. de délai entre deux appels serveur

    def __init__(self, mod, view):
        super().__init__()
        self.ref_mod = mod
        self.ref_view = view

        # self.gameref = glvars.gameref

        # - prepa de quoi changer de mode de jeu...
        self.nextmode_buffer = None
        self._assoc_cchoix_event = {  # TODO fix ! not supposed to use integers 1, 2 here!

            glvars.CHOIX_QUIT: None,  # géré via fonction aussi
            glvars.CHOIX_CRED: 1,  # CgmEvent(EngineEvTypes.PUSHSTATE, state_ident=GameStates.Credits),
            glvars.CHOIX_START: None,  # celui-ci est géré via un evenement BlokuEvents.DemandeTournoi !
            glvars.CHOIX_LOGIN: 2,  # CgmEvent(BlokuEvents.ChoiceChanges),
            # CgmEvent(EngineEvTypes.PUSHSTATE, state_ident=GameStates.Login)
        }

        # - misc
        self.last_pol = None
        self.logged_in = mod.is_logged()
        self.polling_mode = True

        self.serv = None  # TODO fix later, HttpServer.instance()

    def pause_polling(self):
        self.polling_mode = False

    def resume_polling(self):
        self.polling_mode = True

    # --------------------------------------
    #  Gestion des évènements
    # --------------------------------------
    def on_event(self, ev):
        if ev.type == EngineEvTypes.Update:
            if (self.nextmode_buffer is not None) and not util.is_sfx_playin():
                # traitement nextmode_buffer...
                if self.nextmode_buffer == glvars.CHOIX_LOGIN:
                    self.pev(BlokuEvents.DemandeTournoi)
                    self.pev(EngineEvTypes.StatePush, state_ident=defs.GameStates.Puzzle)

                elif self.nextmode_buffer == glvars.CHOIX_QUIT:
                    # if kataen.runs_in_web():
                    #     katapi.clear_local_session()
                    #     glvars.username = None
                    #     glvars.acc_id = None
                    #     self.ref_mod.reset()
                    #     self.logged_in = False
                    #     self.pause_polling()
                    #     self.ref_view.refresh_graphic_state()
                    #     print('*** RESET ok ***')
                    pyv.vars.gameover = True

                # else:
                #     ev = self._assoc_cchoix_event[self.nextmode_buffer]
                #     if ev is not None:
                #         pyv.get_ev_manager().post(ev)
                # reset du champ concerné
                self.nextmode_buffer = None
        elif ev.type == BlokuEvents.Validation:
            self.nextmode_buffer = self.ref_mod.get_curr_choice()

        elif ev.type == EngineEvTypes.Keydown:
            if ev.key == pygame.K_UP:
                self.ref_mod.move(-1)

            elif ev.key == pygame.K_DOWN:
                self.ref_mod.move(1)

            elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.ref_view.validate_effect()
                self.pev(BlokuEvents.Validation)

        # avant, quand yavait un bet
        # ev.type == BlokuEvents.DemandeTournoi:
            # if self.ref_mod.can_bet():
            #     # toute la comm. réseau se passe bien ?
            #     katapi.set_curr_game_id(glvars.GAME_ID)
            #     payment_ok, numero_chall, chall_seed = katapi.pay_for_challenge(glvars.acc_id)
            #     cond1 = self.ref_mod.is_real_login and payment_ok
            #     glvars.num_challenge = numero_chall
            #     glvars.chall_seed = chall_seed
            #     if (not self.ref_mod.is_real_login) or cond1:
            #         self.pev(EngineEvTypes.PUSHSTATE, state_ident=GameStates.Puzzle)
            # else:
            #     print('cant bet says the ctrler')

    def impacte_retour_login(self):
        print('ds impacte_retour_login')
        if glvars.username:
            print('username has been set')
            self.ref_mod.mark_auth_done(glvars.copie_solde)
            self.logged_in = True
            self.ref_view.refresh_graphic_state()
            self.resume_polling()


class TitleScreenState(pyv.BaseGameState):
    """
    represents the game state that shows the game title + a menu!
    """

    def __init__(self, gs_id):
        super().__init__(gs_id)
        self.v = self.m = self.c = None
        self.der_lstate = None

    def enter(self):
        if self.m is None:
            self.m = TitleModel()
        self.v = TitleView(self.m)
        if self.c is None:
            self.c = MenuCtrl(self.m, self.v)
            self.c.impacte_retour_login()

        self.v.turn_on()
        self.c.turn_on()
        util.init_sound()

        # no music!
        # glvars.playmusic()

    def resume(self):
        self.c.impacte_retour_login()
        self.v.turn_on()
        if self.der_lstate != (glvars.username is None):
            self.m.reset_choice()

        self.c.turn_on()

    def release(self):
        self.c.turn_off()
        self.v.turn_off()

        pygame.mixer.music.fadeout(750)
        while pygame.mixer.music.get_busy():
            pass
        print('release( TitleScreenState) ')

    def pause(self):
        self.der_lstate = (glvars.username is None)
        self.c.turn_off()
        self.v.turn_off()
