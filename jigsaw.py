import random

import pygame as pg

from PIL import Image, ImageDraw
from piece import Piece

from config import *


def clamp(min_, value, max_): return min(max_, max(min_, value))


def load_cut_images():
	cuts_folder = PROJECT_FOLDER / "src" / "piece_cuts"

	cuts = list()

	for i in range(1, 9):
		cut_img = pg.image.load(cuts_folder / f"medium_cut{i}.png").convert_alpha()
		cuts.append(cut_img)

	return cuts



def pygame_surface_to_pillow_image(surface):
	"""Converts a Pygame surface to a Pillow Image."""
	data = pg.image.tostring(surface, "RGBA")
	width, height = surface.get_size()
	return Image.frombytes("RGBA", (width, height), data)

def pillow_image_to_pygame_surface(image):
	"""Converts a Pillow Image to a Pygame surface."""
	data = image.tobytes()
	width, height = image.size
	return pg.image.fromstring(data, (width, height), "RGBA")

def flood_fill_pillow(image, start_pos, fill_color):
	"""Applies a flood fill using Pillow."""
	ImageDraw.floodfill(image, start_pos, fill_color)

def flood_fill(surface, start_pos, fill_color):
	# Convert Pygame surface to Pillow Image
	pillow_image = pygame_surface_to_pillow_image(surface)
	
	# Apply flood fill using Pillow
	flood_fill_pillow(pillow_image, start_pos, fill_color)
	
	# Convert the Pillow image back to Pygame surface
	surface = pillow_image_to_pygame_surface(pillow_image)

	return surface


def swap_red_green(surface):
	surface = surface.copy()

	"""Swaps red and green colors in a Pygame surface."""
	width, height = surface.get_size()
	for x in range(width):
		for y in range(height):
			color = surface.get_at((x, y))
			if color[:3] == (255, 0, 0):  # Red (ignoring alpha)
				surface.set_at((x, y), (0, 255, 0, 255))  # Change to green
			elif color[:3] == (0, 255, 0):  # Green
				surface.set_at((x, y), (255, 0, 0, 255))  # Change to red

	return surface


def apply_cut(piece_surf, cuts, piece_id, top=None, bottom=None, left=None, right=None):
	cut_size = cuts[0].get_size()

	piece_surf = piece_surf.copy()
	piece_size = piece_surf.get_size()

	CUT = (0, 255, 0, 255)
	NO_CUT = (255, 0, 0, 255)
	TRANSPARENT = (0, 0, 0, 0)

	piece_mask = piece_surf.copy()
	piece_mask.fill((0, 0, 0, 0))

	# Fill corners
	cut_w = cut_size[0]//2

	piece_mask.fill((0, 255, 0, 255), (0, 0, cut_w, cut_w))
	piece_mask.fill((0, 255, 0, 255), (piece_size[0] - cut_w - 1, 0, cut_w + 1, cut_w))
	piece_mask.fill((0, 255, 0, 255), (0, piece_size[1] - cut_w - 1, cut_w, cut_w + 1))
	piece_mask.fill((0, 255, 0, 255), (piece_size[0] - cut_w - 1, piece_size[1] - cut_w - 1, cut_w + 1, cut_w + 1))

	if top is not None:
		surf_cut = cuts[top]

		w, h = surf_cut.get_size()

		surf_cut = swap_red_green(surf_cut)

		surf_cut = flood_fill(surf_cut, (0, 0), CUT)
		surf_cut = flood_fill(surf_cut, (w-2, 1), NO_CUT)
		surf_cut = flood_fill(surf_cut, (w-2, 1), TRANSPARENT)

		surf_cut = pg.transform.rotate(surf_cut, -90)

		piece_mask.blit(surf_cut, (w//2, 0))


	if bottom is not None:
		surf_cut = cuts[bottom]

		w, h = surf_cut.get_size()

		surf_cut = flood_fill(surf_cut, (w-2, 1), CUT)
		surf_cut = flood_fill(surf_cut, (0, 0), NO_CUT)
		surf_cut = flood_fill(surf_cut, (0, 0), TRANSPARENT)

		surf_cut = pg.transform.rotate(surf_cut, -90)

		piece_mask.blit(surf_cut, (w//2, piece_size[1] - w))


	if left is not None:
		surf_cut = cuts[left]

		w, h = surf_cut.get_size()

		surf_cut = swap_red_green(surf_cut)

		surf_cut = flood_fill(surf_cut, (0, 0), CUT)
		surf_cut = flood_fill(surf_cut, (w-2, 1), NO_CUT)
		surf_cut = flood_fill(surf_cut, (w-2, 1), TRANSPARENT)

		piece_mask.blit(surf_cut, (0, w//2))


	if right is not None:
		surf_cut = cuts[right]

		w, h = surf_cut.get_size()

		surf_cut = flood_fill(surf_cut, (w-2, 1), CUT)
		surf_cut = flood_fill(surf_cut, (0, 0), NO_CUT)
		surf_cut = flood_fill(surf_cut, (0, 0), TRANSPARENT)

		piece_mask.blit(surf_cut, (piece_size[0] - w, w//2))


	for x in range(piece_size[0]):
		for y in range(piece_size[1]):
			if piece_mask.get_at((x, y)).g == 255:
				piece_surf.set_at((x, y), (0, 0, 0, 0))


	piece = Piece(piece_surf, piece_id, cut_size, top=top, left=left, bottom=bottom, right=right)


	return piece




def cut_pieces(bg_surface, cuts):
	background = bg_surface.copy()

	bg_size = background.get_size()

	cut_w, cut_h = cuts[0].get_size()
	piece_size = cut_h + cut_w

	piece_canva = pg.Surface((piece_size, piece_size)).convert_alpha()

	# Pieces along the dimentions
	pieces_w = bg_size[0] // cut_h
	pieces_h = bg_size[1] // cut_h

	side_cuts = {'top': None, 'bottom': None, 'left': None, 'right': None}

	pieces = list()

	for i in range(pieces_w):
		x = cut_h*i - cut_w//2
		clamp_x = clamp(0, x, bg_size[0])

		cut_size_x = piece_size

		if clamp_x + piece_size >= bg_size[0]:
			cut_size_x = bg_size[0] - clamp_x

		side_cuts['left'] = None

		if i > 0 and side_cuts['right'] is not None:
			side_cuts['left'] = side_cuts['right']

		if i + 1 < pieces_w:
			side_cuts['right'] = random.randint(1, len(cuts)-1)
		else:
			side_cuts['right'] = None


		for j in range(pieces_h):
			y = cut_h*j - cut_w//2
			clamp_y = clamp(0, y, bg_size[1])

			cut_size_y = piece_size

			if clamp_y + piece_size >= bg_size[1]:
				cut_size_y = bg_size[1] - clamp_y

			side_cuts['top'] = None

			if j > 0 and side_cuts['bottom'] is not None:
				side_cuts['top'] = side_cuts['bottom']


			if j + 1 < pieces_h:
				side_cuts['bottom'] = random.randint(1, len(cuts)-1)
			else:
				side_cuts['bottom'] = None

			area_cut = (clamp_x, clamp_y, cut_size_x, cut_size_y)
			piece_surf = background.subsurface(area_cut)

			piece_canva.fill((0, 255, 0, 0))
			piece_canva.blit(piece_surf, (clamp_x - x, clamp_y - y))

			piece = apply_cut(piece_canva, cuts, f'{i}_{j}', **side_cuts)

			pieces.append(piece)

	return pieces



















