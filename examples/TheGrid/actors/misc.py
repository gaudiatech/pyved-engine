"""
we actors for the Roguelike here,
except from "maze" and "player", "monsters" that have their own file
"""
import random

from .. import glvars
from ..glvars import pyv


def new_gui():
	data = {'active': False, 'msg': None}

	# -----------
	#  behavior
	def on_player_death(this, ev):
		glvars.game_paused = True
		this.active = True
		ft = pyv.new_font_obj(None, 80)  # large txt
		score = glvars.level_count
		this.msg = ft.render(glvars.ENDGAME_MSG.format(score), False, 'white', 'black')

	def on_draw(this, ev):
		if this.active:
			m_w, m_h = this.msg.get_size()
			scr_w, scr_h = ev.screen.get_size()
			tx, ty = (scr_w - m_w)//2, (scr_h - m_h)//2
			ev.screen.blit(this.msg, (tx, ty))

	def on_game_restart(this, ev):  # means the game resumes
		this.active = False

	return pyv.new_actor('gui', locals())


def new_potion(gpos):
	data = {
		'pos': tuple(gpos), 'effect': random.choice((-30, +50))
	}

	# -----------
	#  behavior
	def on_draw(this, ev):
		item_position = this.pos
		if not pyv.trigger('test', glvars.ref_visibility_mger, item_position):
			return  # avoid drawing invisble things
		adhoc_img = glvars.tileset.image_by_rank(810) \
			if this.effect < 0 else glvars.tileset.image_by_rank(811)
		scr_x, scr_y = item_position[0] * glvars.CELL_SIDE, item_position[1] * glvars.CELL_SIDE
		ev.screen.blit(adhoc_img, (scr_x, scr_y, 32, 32))

	def on_player_movement(this, ev):
		if ev.pos[0] == this.pos[0] and ev.pos[1] == this.pos[1]:
			pyv.trigger('change_hp', glvars.ref_player, this.effect)
			# trick: an actor can destroy itself
			auto_id = pyv.id_actor(this)
			pyv.del_actor(auto_id)
			pyv.post_ev('item_destroyed', id=auto_id)

	return pyv.new_actor('potion', locals())


# --------------- exit ----------------------
def new_exit_entity(pos):
	data = {
		'x': pos[0], 'y': pos[1]  # TODO use .pos like elsewhere ->unification
	}

	# - behavior
	def on_player_movement(this, ev):
		new_avx, new_avy = ev.pos  # test new position vs map exit
		if new_avx == this.x:
			if new_avy == this.y:
				glvars.level_count += 1
				print('you now enter level:', glvars.level_count)
				pyv.post_ev('req_refresh_maze')

	def on_draw(this, ev):
		if not pyv.trigger('test', glvars.ref_visibility_mger, (this.x, this.y)):
			return  # avoid drawing invisble things
		ev.screen.blit(
			glvars.tileset.image_by_rank(1092),
			(this.x * glvars.CELL_SIDE, this.y * glvars.CELL_SIDE, 32, 32)
		)

	return pyv.new_actor('exit_entity', locals())
