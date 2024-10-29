"""
testing the event system rev4
"""
import pyved_engine as pyv

EvManager = pyv.events.EvManager
PseudoEnum = pyv.events.PseudoEnum
EngineEvTypes = pyv.events.EngineEvTypes
game_events_enum = pyv.events.game_events_enum


class SampleListener(pyv.EvListener):
    """
    mockup class
    """
    def __init__(self, nom):
        super().__init__()
        self._avname = nom

    def get_av_name(self):
        return self._avname

    def set_av_name(self, x):
        self._avname = x

    def on_paint(self, ev):
        print('m1 -', self, ev)

    def on_player_death(self, ev):
        print('m1 -', self, ev)

    def on_update(self, ev):
        print('m2 -', self, ev)

    def on_netw_receive(self, ev):
        print('m3 -', self, ev)

    def __str__(self):
        return '<inst. Of SampleListener. Name=' + str(self._avname) + '>'


# -----------------
#  testing
# ----------------
pyv.init()

MyEvents = game_events_enum((
    'PlayerMovement',
    'PlayerDeath'
))

manager = EvManager.instance()
manager.debug_mode = True

# the manager becomes "self-aware", for
# all engine ev types AND all game-specific ev types
manager.setup(MyEvents)

print('~~ codes ~~')
print(EngineEvTypes.Update)
print(EngineEvTypes.Paint)
print('...')
print(EngineEvTypes.NetwReceive)
print('and the extra:')
print(MyEvents.PlayerMovement)
print(MyEvents.PlayerDeath)
print('-' * 48)

# Test: post 5 events and updates the ev manager...
print('method .POST called x5')
manager.post(17, serveur='api.gaudia-tech.com', machin='ouais')
manager.post(3, jojo='trois', nom='tom')
manager.post(551, hp='128', nom='roger')
manager.post(17, hp='11', nom='jojo')
manager.post(332, hp='59878', nom='poisson')

print('the NEW queue size=', manager.queue_size)
manager.update()
print('after .UPDATE call, the queue size=', manager.queue_size)
print('-' * 48)

print('show me the regexp in EventManager inst?')
print(manager.regexp)
print(manager.regexp.match('on_player_movement'))
print('-' * 48)

print("create! then turn on/turn off the listener..")
my_li = SampleListener('thomas')
print('listener id?', my_li.id)
my_li.turn_on()
my_li.turn_off()

# ---for sandbox testing---
pyv.quit()
enum_example = PseudoEnum(['KeyUp', 'KeyDown', 'Update'])
print(enum_example.KeyUp)
