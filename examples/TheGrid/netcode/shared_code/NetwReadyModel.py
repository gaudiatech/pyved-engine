import json

from .ChasersModel import ChasersModel


class NetwReadyModel(ChasersModel):
    def __init__(self, localplayer):
        super().__init__()
        self.localplayer = localplayer

    # GENERIC ++
    # def serialize(self):
    #    raise NotImplementedError
    # def load_state(self, given_serial):
    #    raise NotImplementedError
    def push_changes(self):
        self.pev('x_push_changes', self.serialize())

    def force_sync(self):
        self.pev('x_request_sync')

    # SPECIFIC ++
    def serialize(self):
        return json.dumps(
            {'world': self.world, 'p1': self.score['p1'], 'p2': self.score['p2'], 'winner': self.winner}
        )

    def load_state(self, given_serial):
        # TODO debug that part !!!
        # - dirty fix:
        # When using .SOCKET network layer then,
        # for unknown reasons given_serial is already a dict-type!
        # dico_full = given_serial

        # will work when using websocket transport layer...
        try:
            dico_full = json.loads(given_serial)
        except json.JSONDecodeError as e:
            print('******************************* deserialisation mal passée')
            print('SERIAL:')
            print(given_serial)
            print()
            print()
            raise ValueError

        infos_st = dico_full['world']
        self.taken.clear()
        for lig in range(4):
            for c in range(6):
                code = infos_st[c][lig]
                if code in ('p1', 'p2', 'ai'):
                    self.positions[code] = (c, lig)
                    self.taken.add((c, lig))
                self.world[c][lig] = code
        self.score['p1'] = dico_full['p1']
        self.score['p2'] = dico_full['p2']
        self.winner = dico_full['winner']

    def remote_move_pl(self, c, lig):
        self.pev('x_request_movement', json.dumps([self.localplayer, c, lig]))
    # - Would also work... IF NOT following the authoritative server principle
    # def move_pl(self, sym, ij_target):
    #     super().move_pl(sym, ij_target)
    #     self.push_changes()
