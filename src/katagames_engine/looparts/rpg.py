print('-'*32)
print('kengi [RPG submodule] is being loaded')
print('-'*32)


import math
from math import floor

from ..foundation.defs import Singleton


# from coremon_main import CgmEvent, EventManager
# from coremon_main.Singleton import Singleton
# from defs_bo import const
# from defs_bo.ev_types import MyEvTypes
# from defs_bo.fighter_stats import PrimaryStats, SecStats
# from tools.op_cfg_file import dico_repr_from_cfg_file


CODE_FULL_LIFE = -9999


class Character:
    def __init__(self, cname, **kwargs):
        pass


class Weapon:
    def __init__(self, cname, **kwargs):
        pass


@Singleton
class StatsFramework:

    MAX_LEVEL = 90  # pour tt combattant
    NIV_PALIERS = [5 * k for k in range(1, 18 + 1)]

    NIVEAU_VERS_XP = None
    XP_VERS_NIVEAU = None

    def __init__(self):

        if self.NIVEAU_VERS_XP is None:  # si classe pas initialisée...

            cst = 300
            self.NIVEAU_VERS_XP = {
                1: 0,
                2: cst,  # const
                3: 900,  # prec + 2 * const
                4: 1800,  # prec + 3 * const
                # etc. jusque le MAX_LEVEL
            }
            for k in range(5, self.MAX_LEVEL + 1):
                self.NIVEAU_VERS_XP[k] = self.NIVEAU_VERS_XP[k - 1] + cst * (k - 1)

            self.XP_VERS_NIVEAU = dict()  # le lien fait dans l'autre sens peut-être utile aussi
            for level, xp_req in self.NIVEAU_VERS_XP.items():
                self.XP_VERS_NIVEAU[xp_req] = level

    def get_niveau_max(self):
        return self.MAX_LEVEL

    def get_paliers(self):
        return self.NIV_PALIERS

    def build_stats(self, local_av: bool, curr_hp, xp_pts, bonus_eq):
        return _Stats(local_av, curr_hp, xp_pts, bonus_eq)

    def get_xp_pour_niveau(self, n):
        return self.NIVEAU_VERS_XP[n]

    def level_from_xp(self, montant_xp):
        paliers_ord = list(self.XP_VERS_NIVEAU.keys())
        paliers_ord.sort()
        paliers_ord.reverse()  # classement du + grand au - grand
        for p in paliers_ord:
            if montant_xp >= p:  # palier atteint
                return self.XP_VERS_NIVEAU[p]
        raise Exception('anomalie méthode determineNiveau')

    def level_to_xp(self, n):
        return self.NIVEAU_VERS_XP[n]

    def det_xp_for_level(self, target_level):
        for xp_amount, niveau in self.XP_VERS_NIVEAU.items():
            if target_level == niveau:
                return xp_amount
        return None


class StatsKern:
    """
    modélise les statistiques de combat d'un personnage
    - contient l'info. de niveau & calcule tous les bonus liés au niveau
    - contient l'info. de stats bonus reçues de l'extérieur
    """

    def __init__(self, local_av, curr_hp, xp_pts, bonus_eq, caps_n_hp, tuple_params_progres, tuple_params_atk):
        self.ev_st_change = CgmEvent(MyEvTypes.StatsChange, local_av=local_av)

        self.armor_class_cap, self.lifesteal_cap, self.hp_per_en = caps_n_hp
        self.en_per_thr, self.st_per_thr, self.pe_per_thr, self.sa_per_thr, self.wp_per_thr = tuple_params_progres
        self.alpha, self.beta, self.gamma = tuple_params_atk

        self.base_stats = dict()
        self.effectiv_stats = None

        self.__curr_focus = 0

        self.__curr_hp = curr_hp
        self.__curr_xp = xp_pts

        self._manager = EventManager.instance()  # TODO hériter de CogObject & utiliser .pev

        level_adhoc = StatsFramework.instance().level_from_xp(xp_pts)
        self.bonus_eq = None
        self.__level = None
        self.__impacte_stats(level_adhoc, bonus_eq)

        if self.__curr_hp is None:
            self.__curr_hp = self._det_stat_secondaire(SecStats.MaxHp)

    def det_ratio_for_levelup(self):
        """
        :return: un flotant compris entre 0 et 1, à deux chiffres significatifs
        """
        fram = StatsFramework.instance()
        borne_inf = fram.level_to_xp(self.__level)
        borne_sup = fram.level_to_xp(self.__level + 1)

        if borne_sup is None:
            tmp = 0
        else:
            q = self.__curr_xp - borne_inf
            res = q / (borne_sup - borne_inf)
            tmp = math.floor(res * 100)

        return tmp / 100  # à deux chiffers significatifs

    def __impacte_stats(self, nouveau_level, nouveau_bonus_eq):
        self.__level = nouveau_level

        # --- calcul des stats de base
        for st_code in PrimaryStats.all_codes:
            self.base_stats[st_code] = 1

        for p in StatsFramework.instance().get_paliers():
            if self.__level < p:
                break

            # bonus identique attribué à chaque dépassement de palier
            self.base_stats[PrimaryStats.Endurance] += self.en_per_thr
            self.base_stats[PrimaryStats.Strength] += self.st_per_thr
            self.base_stats[PrimaryStats.Perception] += self.pe_per_thr
            self.base_stats[PrimaryStats.Sadism] += self.sa_per_thr
            self.base_stats[PrimaryStats.Willpower] += self.wp_per_thr

        self.set_bonus_eq(nouveau_bonus_eq)

    def set_bonus_eq(self, bonus_eq):
        self.bonus_eq = bonus_eq
        self.effectiv_stats = self.base_stats.copy()

        for code_st, val in bonus_eq.items():
            if code_st not in self.effectiv_stats:
                self.effectiv_stats[code_st] = bonus_eq[code_st]

            elif code_st == PrimaryStats.Sadism:
                self.effectiv_stats[PrimaryStats.Sadism] += bonus_eq[PrimaryStats.Sadism]

            else:
                self.effectiv_stats[code_st] += bonus_eq[code_st]

        self._manager.post(self.ev_st_change)

    def get_xp(self):
        return self.__curr_xp

    def hack_inject_level(self, n):
        quantite_requise = StatsFramework.instance().level_to_xp(n)
        self._set_xp(quantite_requise)

    def stack_xp(self, amount: int):
        """
        :param amount: quantité entière d'xp, strictement supérieur
        :return: int si nouveau level/None sinon
        """
        assert amount > 0
        res = self._set_xp(self.__curr_xp + amount)
        return res

    def _set_xp(self, amount):
        prior_level = self.get_level()
        self.__curr_xp = amount
        post_level = StatsFramework.instance().level_from_xp(self.__curr_xp)

        evt_m = EventManager.instance()

        if prior_level != post_level:
            self.__impacte_stats(post_level, self.bonus_eq)  # provoque evt stats change
            self.__level = post_level
            evt_m.post(CgmEvent(MyEvTypes.AvatarLevelsUp, new_level=post_level))
            return post_level

        adhoc_ev = CgmEvent(MyEvTypes.StatsChange)
        evt_m.post(adhoc_ev)

    def get_level(self):
        return self.__level

    def get_increm_focus(self):
        return self._det_stat_secondaire(SecStats.PowerIncrem)

    def getCurrFocus(self):
        return self.__curr_focus

    def check_hp_filled(self):
        return self.__curr_hp == self._det_stat_secondaire(SecStats.MaxHp)

    def getHp(self):
        if self.__curr_hp == CODE_FULL_LIFE:  # TODO généraliser usage, évite au joueur de se blesser en changeant eq.
            return self.get_value(SecStats.MaxHp)
        return self.__curr_hp

    def stackHp(self, val, bool_cap_hp=True):
        before = self.getHp()
        after = before + val
        self.set_hp(after)
        if bool_cap_hp:
            self.capHp()

    def set_hp(self, val):
        assert isinstance(val, int)
        self.__curr_hp = val
        self._manager.post(self.ev_st_change)

    def shred_hp(self, ratio):
        # shred= diminue les pv suivant un ratio des pv max

        cap = self.get_value(SecStats.MaxHp, True)
        dmg = int(ratio * cap)
        if const.DEV_MODE:
            print('loosing {} hp'.format(dmg))
        self.set_hp(self.getHp() - dmg)

    def is_alive(self):
        return self.getHp() > 0

    def capHp(self):
        bsup = self.get_value(SecStats.MaxHp, True)
        if self.__curr_hp > bsup:
            self.__curr_hp = bsup
            self._manager.post(self.ev_st_change)

    def add_focus(self, val: int):
        self.__curr_focus += val

        if self.__curr_focus > const.FOCUS_MAX:
            self.__curr_focus = const.FOCUS_MAX

        self._manager.post(self.ev_st_change)

    def has_full_focus(self):
        return self.__curr_focus == const.FOCUS_MAX

    def nullify_focus(self):
        self.__curr_focus = 0
        self._manager.post(self.ev_st_change)

    def set_max_focus(self, val):
        self.__max_focus = val
        res = False
        if self.__curr_focus >= self.__max_focus:
            self.__curr_focus %= self.__max_focus
            res = True
        self._manager.post(self.ev_st_change)
        return res

    def reset_focus_state(self):
        self.set_max_focus(const.FOCUS_MAX)
        self.nullify_focus()

    # ----------------------------------
    #  MÉTIER
    # ----------------------------------
    def _det_stat_secondaire(self, stat_code):
        """
        :param stat_code:

        - paliers pour PowerIncrem
        willpower=1 y=1
        willpower=8 y=2
        willpower=19 y=3
        willpower=36 y=4
        willpower=65 y=5
        willpower=113 y=6
        willpower=192 y=7
        willpower=323 y=8

        :return:
        """

        if stat_code == SecStats.MaxHp:
            en = self.get_value(PrimaryStats.Endurance, True)
            y = 92
            y += self.hp_per_en * en
            return y

        if stat_code == SecStats.BaseDmg:
            fo = self.get_value(PrimaryStats.Strength, True)
            y = self.alpha + floor((self.beta*fo - 1) / (fo + self.gamma))
            return y

        if stat_code == SecStats.ArmorClass:
            pe = self.get_value(PrimaryStats.Perception, True)
            y = floor(math.log(400 * (pe ** 4), 2)) - 8
            if y > self.armor_class_cap:
                y = self.armor_class_cap
            return y

        if stat_code == SecStats.LifeSteal:
            sa = self.get_value(PrimaryStats.Sadism, True)
            y = math.log(1 + (sa / 196), 2) - 0.01
            if y < 0:
                y = 0.0
            elif y > self.lifesteal_cap:
                y = self.lifesteal_cap
            else:
                y = round(y, 2)
            return y

        if stat_code == SecStats.PowerIncrem:
            x = self.get_value(PrimaryStats.Willpower, True)
            g = 2* math.log((x+9)*0.1)  # retourne des valeurs dans l'intervalle 0-7
            if g > 7:
                g = 7
            y = 1 + floor(g)
            return y

        msg = 'invalid stat_code= {} for _det_stat_secondaire'.format(stat_code)
        raise ValueError(msg)

    # - accesseur NOUVEAU STYLE (juillet 2019)
    def get_value(self, stat_code: int, with_buff=True):
        if stat_code in SecStats.all_codes:
            return self._det_stat_secondaire(stat_code)

        if stat_code not in PrimaryStats.all_codes:
            msg = 'invalid stat_code= {} for _det_stat_primaire'.format(stat_code)
            raise ValueError(msg)

        if with_buff:
            res = self.effectiv_stats[stat_code]
        else:
            res = self.base_stats[stat_code]
        return res


class _Stats(StatsKern):
    params_fins = None

    def __init__(self, local_av: bool, curr_hp, xp_pts, bonus_eq):
        if self.params_fins is None:
            self.params_fins = dico_repr_from_cfg_file(const.FICHIER_STATS_PARAM)

        d = self.params_fins
        print('**********------------------*************--------------')
        print(str(d))
        tuple0 = (d['ac_cap'], d['ls_cap'], d['hp_per_en'])
        tupel1 = (d['en_per_thr'], d['st_per_thr'], d['pe_per_thr'], d['sa_per_thr'], d['wp_per_thr'])
        tupel2 = (d['alpha'], d['beta'], d['gamma'])

        super().__init__(local_av, curr_hp, xp_pts, bonus_eq, tuple0, tupel1, tupel2)
