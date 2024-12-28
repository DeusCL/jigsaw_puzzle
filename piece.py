import pygame as pg
from config import *


class Piece:
	def __init__(self, surface, top=None, left=None, bottom=None, right=None):
		self.app = None

		self.pos = 0, 0
		self.z_index = 0

		self.surface = surface
		self.sides = {'top': top, 'left': left, 'bottom': bottom, 'right': right}
		self.angle = 0
		self.w, self.h = self.surface.get_size()

		self.targeting = False


	def colliding(self, pos):
		rel_x, rel_y = self.get_relpos(pos)

		if rel_x <= 0 or rel_x >= self.w or rel_y <= 0 or rel_y >= self.h:
			return False

		if self.surface.get_at((rel_x, rel_y)).a > 1:
			return True

		return False


	def get_relpos(self, pos):
		x, y = self.pos
		tx, ty = pos

		return tx-x, ty-y


	def update(self):
		mpos = self.app.mpos

		self.targeting = self.colliding(mpos)



