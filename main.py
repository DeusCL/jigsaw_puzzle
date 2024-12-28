import pygame as pg
import sys

from config import *
from scene import Scene

class App:
    def __init__(self):
        pg.init()

        self.screen = pg.display.set_mode(SCREEN_SIZE)
        pg.display.set_caption("Jigsaw Puzzle")

        self.clock = pg.time.Clock()
        self.time = 0

        self.mpos = pg.mouse.get_pos()
        self.scene = Scene(self)

        self.load_cursors()


    def new_cursor(self, cursor_filepath, hotspot=None):
        hotspot = (8, 8) if hotspot is None else hotspot

        new_cursor_img = pg.image.load(cursor_filepath)
        return pg.cursors.Cursor(hotspot, new_cursor_img)


    def load_cursors(self):
        self.cursors = {
            CURSOR_NORMAL: pg.cursors.Cursor(pg.SYSTEM_CURSOR_ARROW),
            CURSOR_HAND_FINGER: pg.cursors.Cursor(pg.SYSTEM_CURSOR_HAND),
            CURSOR_HAND_OPEN: self.new_cursor(CURSOR_HAND_OPEN_FILEPATH),
            CURSOR_HAND_CLOSED: self.new_cursor(CURSOR_HAND_CLOSED_FILEPATH),
            CURSOR_TEXT_MARKER: self.new_cursor(CURSOR_TEXT_MARKER_FILEPATH)
        }

        self.current_cursor = CURSOR_NORMAL


    def render(self):
        self.screen.fill(SKY_COLOR)
        self.scene.render(self.screen)
        pg.display.flip()


    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                pg.quit()
                sys.exit()

            self.scene.handle_event(event)


    def update(self):
        self.current_cursor = CURSOR_NORMAL

        self.time = self.clock.tick(TARGET_FPS)*0.001
        self.mpos = pg.mouse.get_pos()

        self.scene.update()


    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.render()

            self.clock.tick(TARGET_FPS)*0.001
            
            pg.mouse.set_cursor(self.cursors[self.current_cursor])
            pg.display.set_caption(f"{self.clock.get_fps():.2f}")


def main():
    app = App()
    app.run()




if __name__ == '__main__':
    main()



