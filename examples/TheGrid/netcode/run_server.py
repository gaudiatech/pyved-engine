import time


def exec(**kwargs):
    print("run_server.py: Starting the server NOW...")
    from .shared_code import glvars

    # Insert your server initialization and main loop logic here.
    # For example, setting up network connections, initializing services, etc.

    # handy linking.
    # But could it work with trascrypt'pragmas'?
    # from netw_socket_serv import *
    # precursor = {
    #     'get_server_flag': get_server_flag,     # server-side, its like a constant but ok we need it
    #     'start_comms': start_comms,             # called in the server's body -->ok can stay pure JS
    #     'broadcast': broadcast,                 # called by UMediator only. Line 76
    #     'register_mediator': register_mediator  # called only by UMediator line 15, so mediator can receive post call in return
    # }
    # class Objectifier:
    #     def __init__(self, **entries):
    #         self.__dict__.update(entries)
    # netw_layer = Objectifier(**precursor)
    # --- end handy linking ---
    pyv = glvars.pyv

    neotech = pyv.umediator
    netlayer_type = 'socket'
    if 'mode' in kwargs:
        if 'ws'==kwargs['mode']:
            netlayer_type = 'ws'
    netw_layer = pyv.netlayer_factory.build_netlayer(
        netlayer_type, 'server'  # this line is where we choose what netw transport layer we are using
    )
    glvars.mediator = mediator = neotech.UMediator()  # new kind of mediator
    mediator.set_network_layer(netw_layer)  # bind mediator to this netw transport layer!

    # it's only after binding that we can call "start_comms",
    # otherwise the list of mediators is an empty list
    netw_layer.start_comms(kwargs['host'], kwargs['port'])

    from .Server import Server
    serv_obj = Server(**kwargs)

    ff = 1
    cpt = 100
    stop_serv = False
    while not stop_serv:
        try:  # this try...except block is MANDATORY if you wish to be able to exit via Ctrl+C
            serv_obj.proc_server_logic(time.time())
            glvars.mediator.update(True)  # saving cycles will send updates less frequently which can avoir sync errors
            # on socket interface, but creates a bit of lag
            cpt -= 1
            if cpt <= 0:
                ff = ff ^ 1  # flip bit
                print('  .tick. ' if ff else ' .tac. ')
                cpt = 100
            time.sleep(0.1)
        except KeyboardInterrupt as e:
            print('now exiting...')
            stop_serv = True
    # after leaving the refresh loop, one also, NEEDS to close socket, bc it is blocking reads
    print('do: comms->shutdown command on the netw_layer...')
    netw_layer.shutdown_comms()
 