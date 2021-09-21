import katagames_sdk.capsule.engine_ground.conf_eng as cgmconf


stored_pygame_pym = None
stored_web_ctx = None
stored_upscaling = None
diplayrdy = False


def config_display(pygame_pym, runnin_in_web, upscaling_val):
    global stored_pygame_pym, stored_web_ctx, stored_upscaling, diplayrdy
    diplayrdy = True
    stored_pygame_pym = pygame_pym
    stored_web_ctx = runnin_in_web
    stored_upscaling = upscaling_val


def display_update():
    global stored_pygame_pym, stored_web_ctx, stored_upscaling, diplayrdy

    if not diplayrdy:
        raise ValueError('display isnt ready (bad initialization)')

    if not stored_web_ctx:

        if stored_upscaling is None:
            cgmconf.my_pygame_scr.blit(cgmconf.virtual_screen_surf, (0, 0))

        elif int(stored_upscaling) == 2:

            stored_pygame_pym.transform.scale2x(cgmconf.virtual_screen_surf, cgmconf.my_pygame_scr)
        elif int(stored_upscaling) == 3:

            stored_pygame_pym.transform.scale(cgmconf.virtual_screen_surf, cgmconf.CONST_SCR_SIZE, cgmconf.my_pygame_scr)

        stored_pygame_pym.display.update()

    else:
        ctx = cgmconf.browser_canvas.getContext('2d')
        ctx.clearRect(0, 0, cgmconf.CONST_SCR_SIZE[0], cgmconf.CONST_SCR_SIZE[1])
        ctx.drawImage(cgmconf.buffer_canvas, 0, 0)

    # manage upscaling
    # rf = False
    # if not _in_web_context:
    #     if adhoc_upscaling is not None:
    #         pygame.transform.scale(draw_surf, CONST_SCR_SIZE, pygame_screen)
    #         rf = True
