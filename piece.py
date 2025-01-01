import pygame as pg
from config import *


class Piece:
	def __init__(self, surface, id, cut_size, top=None, left=None, bottom=None, right=None):
		self.id = id

		self.app = None

		self.pos = 0, 0
		self.z_index = 0

		self.cut_size = cut_size

		self.surface = surface
		self.sides = {'top': top, 'left': left, 'bottom': bottom, 'right': right}
		self.angle = 0
		self.w, self.h = self.surface.get_size()

		self.targeting = False

		self.debug = False


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
	

	def get_center(self):
		x, y = self.pos
		return x + self.w//2, y + self.h//2


	def update(self):
		mpos = self.app.mpos

		self.targeting = self.colliding(mpos)
	

	def render(self, surface):
		surface.blit(self.surface, self.pos)
		
		if self.debug:
			x, y = self.pos
			cut_w, cut_h = self.cut_size

			pg.draw.circle(surface, (0, 0, 255), self.get_center(), 4)
			pg.draw.circle(surface, (0, 255, 0), (x + cut_w//2, y + cut_w//2), 4)
			pg.draw.rect(surface, (255, 0, 0), (x, y, self.w, self.h), 1)
			# pg.draw.rect(surface, (0, 0, 255), (rx, ry))





