import sys
import json
import time

import pygame as pg

from config import *
from scene import Scene
from client import Client
from player import Player



class App:
    def __init__(self):
        pg.init()

        self.screen = None

        self.clock = pg.time.Clock()
        self.time = 0
        self.dt = 1/60.0

        self.mpos = pg.mouse.get_pos()
        self.scene = Scene(self)

        self.client = Client(self)
        self.player = Player()

        self.font = pg.font.SysFont(GAME_FONT, GAME_FONT_SIZE)

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

        for player_address, player_data in self.client.foreign_players.items():
            pos = player_data.get('mpos')
            nick = player_data.get('nick')

            if not (pos and nick):
                continue

            pg.draw.circle(self.screen, (255, 0, 0), pos, 20)

            # Render the nickname text
            text_surface = self.font.render(nick, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(pos[0], pos[1] - 25))

            # Draw the text on the screen
            self.screen.blit(text_surface, text_rect)

        pg.display.flip()


    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                pg.quit()
                sys.exit()
            
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_TAB:
                    print("Player list:")
                    print(f" - {self.player.nick}: {self.mpos}")
                    for player_address, player_data in self.client.foreign_players.items():
                        print(f" - {player_data['nick']}: {player_data['mpos']}")

            self.scene.handle_event(event)


    def update(self):
        self.current_cursor = CURSOR_NORMAL

        self.time = pg.time.get_ticks()*0.001

        mpos = pg.mouse.get_pos()

        if mpos != self.mpos:
            self.mpos = pg.mouse.get_pos()
            self.client.prepare({"player": {"mpos": self.mpos}})

        self.scene.update()


    def initialize_window(self):
        self.screen = pg.display.set_mode(SCREEN_SIZE)
        pg.display.set_caption("Jigsaw Puzzle")


    def run(self, host=None, port=50000):
        if host is not None:
            self.player.nick = input("Enter your nickname: ")
            self.initialize_window() # This must be called before scene.load_jigsaw

            # Try to connect to the server
            self.client.connect(host, port)

            if not self.client.connected:
                print("Aborting everything.")
                return

        else:
            self.initialize_window()
            self.scene.load_jigsaw(PROJECT_FOLDER / 'src' / 'images' / 'sample2.png')


        while True:
            self.handle_events()
            self.update()
            self.render()

            pg.mouse.set_cursor(self.cursors[self.current_cursor])
            self.clock.tick(TARGET_FPS)
            pg.display.set_caption(f"{self.clock.get_fps():.2f}")


def main():
    app = App()
    app.run()



if __name__ == '__main__':
    main()


