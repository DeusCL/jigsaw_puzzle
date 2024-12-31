import pygame as pg
from config import *

import jigsaw
import random

class Scene:
	def __init__(self, app):
		self.app = app

		self.pieces = list()

		self.max_z_index = 0

		self.target_piece = None
		self.grabbing_piece = None
		self.grabbing_pos = 0, 0
		self.grabed_nothing = False


	def load_jigsaw(self, background_img, seed=1):
		random.seed(seed)

		bg = pg.image.load(background_img)

		cuts = jigsaw.load_cut_images()

		self.pieces = jigsaw.cut_pieces(bg, cuts)

		# Shuffle
		for idx, piece in enumerate(self.pieces):
			piece.pos = random.randint(10, SCREEN_SIZE[0]-100), random.randint(10, SCREEN_SIZE[1]-100)
			piece.z_index = idx

			piece.app = self.app
			self.max_z_index = idx


	def handle_event(self, event):
		if event.type == pg.MOUSEBUTTONUP:
			# Release piece
			self.grabbing_piece = None
			self.grabbing_pos = 0, 0
			self.grabed_nothing = False


	def update(self):
		if self.grabbing_piece is not None:
			self.app.current_cursor = CURSOR_HAND_CLOSED

		for piece in self.pieces:
			piece.update()
	

	def get_piece(self, id):
		for piece in self.pieces:
			if piece.id == id:
				return piece


	def render(self, main_surface):
		self.target_piece = None

		for piece in sorted(self.pieces, key=lambda p: p.z_index):
			main_surface.blit(piece.surface, piece.pos)

			if piece.targeting:
				self.target_piece = piece

		if self.target_piece is not None and not self.grabed_nothing:
			self.app.current_cursor = CURSOR_HAND_OPEN

			if pg.mouse.get_pressed()[0]:
				self.app.current_cursor = CURSOR_HAND_CLOSED

				if self.grabbing_piece is None:
					self.grabbing_piece = self.target_piece

					self.grabbing_pos = self.grabbing_piece.get_relpos(self.app.mpos)

		elif pg.mouse.get_pressed()[0] and not self.grabed_nothing:
			self.grabed_nothing = True

		if self.grabbing_piece is not None:
			dx, dy = self.grabbing_pos
			mx, my = self.app.mpos

			self.grabbing_piece.pos = mx - dx, my - dy


