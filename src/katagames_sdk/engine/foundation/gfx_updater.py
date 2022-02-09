from . import conf_eng as cgmconf


def display_update():

    if cgmconf.runs_in_web:
        # ---------------
        #  runs in Web
        # ---------------
        pass
        # performs the upscaling only if the game runs in local ctx...
        # otherwise the job is already done in JS code+wrapper.py

    else:
        # ---------------
        #  runs in ctx Win/Mac
        # ---------------
        pygame = cgmconf.pygame
        realscreen = pygame.display.get_surface()
        if 1 == cgmconf.get_upscaling():
            realscreen.blit(cgmconf.screen, (0, 0))
        else:
            pygame.transform.scale(cgmconf.screen, cgmconf.CONST_SCR_SIZE, realscreen)
        pygame.display.update()
