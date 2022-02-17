import sys
import traceback

from .foundation.structures import Singleton
from .foundation.util import underscore_format


@Singleton
class StContainer:
    """
    contient toutes les instances de classes qui dérivent de BaseGameState
    """
    def __init__(self):
        self.__setup_done = False
        self.assoc_id_state_obj = dict()

    def hack_bios_state(self, gs_obj):
        self.assoc_id_state_obj[-1] = gs_obj

    def setup(self, enum_game_states, stmapping, pymodule):
        self.__setup_done = True

        if -1 in stmapping.keys():
            gs_obj = stmapping[-1]  # KataFrameState(-1, 'KataFrame')
            gs_obj.glvars_module = pymodule
            self.hack_bios_state(gs_obj)

        # -- initialisation d'après ce qu'on recoit comme enumeration...
        for id_choisi, nom_etat in enum_game_states.inv_map.items():
            nom_cl = nom_etat + 'State'

            if stmapping:  # but = charger en mémoire la classe
                adhoc_cls = stmapping[nom_cl]  # class has been provided

                obj = adhoc_cls(id_choisi, nom_etat)
                self.assoc_id_state_obj[id_choisi] = obj
            else:
                pymodule_name = underscore_format(nom_etat)
                pythonpath = 'app.{}.state'.format(pymodule_name)
                print('StContainer is loading a new game state...')
                try:
                    pymodule = __import__(pythonpath, fromlist=[nom_cl])
                    adhoc_cls = getattr(pymodule, nom_cl)  # class has been retrieved -> ok

                    obj = adhoc_cls(id_choisi, nom_etat)
                    self.assoc_id_state_obj[id_choisi] = obj

                except ImportError as exc:
                    print('adhoc module name(conv. to underscore format)={}'.format(pymodule_name))
                    print('full path for finding class={}'.format(pythonpath))
                    print('target class={}'.format(nom_cl))
                    print('WEB CONTEXT WARNING: make sure you dont have a file named app.py in your project!')
                    sys.stderr.write("Error: failed to import class {} (info= {})\n".format(nom_cl, exc))
                    traceback.print_last()

    def retrieve(self, identifiant):
        """
        :param identifiant: peut-être aussi bien le code (int) que le nom de classe dédiée (e.g. PlayState)
        :return: instance de BaseGameState
        """

        # construction par nom ou identifiant entier
        # TODO rétablir recherche par nom et non par code...

        # if isinstance(identifiant, str):
        #     gamestate_id = None
        #     for num_id, nom in state_listing.items():
        #         if nom == identifiant:
        #             gamestate_id = num_id
        #             break
        #     if gamestate_id is None:
        #         assert 0, "state name not found: " + identifiant
        # else:
        #     gamestate_id = identifiant
        gamestate_id = identifiant
        return self.assoc_id_state_obj[gamestate_id]
