import pygame as pg
import pygame.gfxdraw

from config import SCREEN_SIZE, ASSETS_DIR

from piece import Piece


class Board:
    def __init__(self, app):
        self.app = app
        self.texture = pg.image.load(ASSETS_DIR / 'board.png')
        self.size = None
        self.frame_thickness = 3


    def nearest(self, point, grid_size, origin=(0, 0)):
        px, py = point
        w, h = grid_size
        ox, oy = origin

        grid_x = round((px - ox) / w) * w + ox
        grid_y = round((py - oy) / h) * h + oy

        return (grid_x, grid_y)
    

    def get_pos(self):
        x = 20
        y = SCREEN_SIZE[1]//2 - self.size[1]//2
        return x, y


    def drop_in(self, piece: Piece):
        if not piece:
            return

        # Verify if the piece is inside this board
        x, y = self.get_pos()
        w, h = self.size
        cx, cy = piece.get_center()

        is_inside = cx >= x and cx < x + w and cy >= y and cy < y + h

        if not is_inside:
            return

        cut_w, cut_h = piece.cut_size[0], piece.cut_size[1]

        rx, ry = piece.pos[0] - x, piece.pos[1] - y

        piece.pos = x + round((rx+cut_w/2)/cut_h)*cut_h - cut_w//2, y + round((ry+cut_w/2)/cut_h)*cut_h - cut_w//2

        self.app.client.prepare({"player": {"piece": {"id":piece.id, "pos": piece.pos}}})


    def render(self, surface):
        if not self.size:
            return

        x, y = self.get_pos()
        w, h = self.size

        rx = x - self.frame_thickness
        ry = y - self.frame_thickness
        rw = w + 2*self.frame_thickness
        rh = h + 2*self.frame_thickness

        pg.draw.rect(surface, (255, 255, 255), (rx, ry, rw, rh), self.frame_thickness)
        pygame.gfxdraw.textured_polygon(surface, [(x, y), (x + w - 1, y), (x + w - 1, y + h - 1), (x, y + h - 1)], self.texture, 0, 0)



