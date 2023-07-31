"""
Project - Python Chess
(c) All rights reserved | Code LICENCE = GNU GPL

This is a joint work. Authors are:

- Steve Osborne (the very first prototype, encoding game rules)
   [contact: srosborne_at_gmail.com]

- Thomas Iwaszko (port to python3+kengi, game improvement)
   [contact: thomas.iw@kata.games]
"""
import chdefs
import pyved_engine as pyv
from chdefs import ChessGstates
from chessintro import ChessintroState
from chessmatch import ChessmatchState


class DummyCls(pyv.GameTpl):
    def get_video_mode(self):
        return pyv.HIGHRES_MODE

    def list_game_events(self):
        return chdefs.ChessEvents

    def list_game_states(self):
        mapping = {  # do this to bind state_id to the ad-hoc class!
            ChessGstates.Chessintro: ChessintroState,
            ChessGstates.Chessmatch: ChessmatchState
        }
        return ChessGstates, mapping


chdefs.ref_game_obj = game_obj = DummyCls()
game_obj.loop()
