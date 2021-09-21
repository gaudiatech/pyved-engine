
VERSION = version = '0.0.6'
CONST_SCR_SIZE = (960, 540)
_in_web_context = None

_upscaling_factor = 1.0

virtual_screen_surf = None  # ref to Surface

# for the web
buffer_canvas = None
browser_canvas = None


def set_buffercanvas(jsobj):
    global buffer_canvas
    buffer_canvas = jsobj


def conv_to_vscreen(x, y):
    global _upscaling_factor
    return int(x/_upscaling_factor), int(y/_upscaling_factor)


def set_browsercanvas(jsobj):
    global browser_canvas
    browser_canvas = jsobj

# for local exec (real pygame)
my_pygame_scr = None
def set_realpygame_screen(ref_surf):
    global my_pygame_scr
    my_pygame_scr = ref_surf


def renseigne(bool_v):
    global _in_web_context
    _in_web_context = bool_v


def set_vscreen(ref_surface, upscaling):
    global virtual_screen_surf, _upscaling_factor, browser_canvas, my_pygame_scr
    virtual_screen_surf = ref_surface

    if upscaling:
        _upscaling_factor = upscaling

    if _upscaling_factor > 1:
        if _in_web_context:
            print('upscaling x{}'.format(_upscaling_factor))
            ctx = browser_canvas.getContext('2d')
            ctx.imageSmoothingEnabled = False
            ctx.scale(_upscaling_factor, _upscaling_factor)
        else:
            if my_pygame_scr is None:
                raise ValueError('plz use set_realpygame_screen(...) FIRST!')


def runs_in_web():
    global _in_web_context
    if _in_web_context is None:
        raise ValueError('wrong init of module conf_eng')
    return _in_web_context


def get_screen():
    global virtual_screen_surf
    return virtual_screen_surf
