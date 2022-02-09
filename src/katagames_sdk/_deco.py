

linkto_web_entry_point = None
linkto_web_animate = None

# default mode = local execution -----
runs_in_web = False


def _inert_decorator(fnc):
    return fnc


web_animate = web_entry_point = _inert_decorator


# special mode = web ctx execution -----
if '__BRYTHON__' in globals():
    from browser import window as _w

    runs_in_web = True

    def _my_decorator0(fnc):
        global linkto_web_entry_point
        print(' [web_entry_point] - found a link')
        linkto_web_entry_point = fnc
        _w.entryPoint = fnc
        return fnc

    def _my_decorator1(fnc):
        global linkto_web_animate
        print(' [web_animate] - found a link')
        linkto_web_animate = fnc
        _w.kataAnimate = fnc
        return fnc

    web_animate = _my_decorator1
    web_entry_point = _my_decorator0
