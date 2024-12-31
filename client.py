import socket
import json
import time
import random
import threading

from config import PROJECT_FOLDER, DATA_DELAY
from utils import send, receive, recursive_update


class Client:
    def __init__(self, app):
        self.app = app
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.connected = False
        
        # This dict will contain the nickname of the players as the key
        # and as the values will be another dict containing 'mpos' and 'piece'
        # where 'mpos' is the mouse position of the foreing player, and 'piece'
        # the piece bein grabbed by the player
        self.foreign_players = {}

        self.data_to_send = {}


    def update_piece(self, piece_data):
        piece = self.app.scene.get_piece(piece_data['id'])
        piece.pos = piece_data['pos']


    def process_message(self, message):
        if not message:
            return

        if "pieces" in message:
            # Update a bunch of pieces
            pieces_data = message.get("pieces")
            print(f"Updating {len(pieces_data)} pieces at once...")
            for piece_data in pieces_data:
                self.update_piece(piece_data)

        elif "players" in message:
            # Update a player
            incoming_data_player = message.get("players")

            for data_player in incoming_data_player:
                address = data_player.get("address")
                nick = data_player.get("nick")
                mpos = data_player.get("mpos")

                if not address or not nick or not mpos:
                    return

                self.foreign_players[address] = {"nick": nick, "mpos": mpos}


    def listen_carefully(self):
        print("Listening carefully to the server...")

        while True:
            try:
                data = receive(self.sock)

                try:
                    self.process_message(data)
                except Exception as error:
                    print(f"Error en el procesar mensaje: {error}")

            except ConnectionResetError as error:
                print(f"Connection lost with the server: {error}")
                break
                
            except ConnectionError as error:
                print(f"Connection error: {error}")
                break

            except json.JSONDecodeError as error:
                print(f"JSON decodification error: {error}")
                print("Skipping data received.")

        self.connected = False
        self.sock.close()
    

    def prepare(self, data):
        recursive_update(self.data_to_send, data)


    def data_sender(self):
        print("Initializing data sender...")

        while True:
            if len(self.data_to_send) == 0:
                time.sleep(DATA_DELAY)
                continue

            self.send(self.data_to_send)
            self.data_to_send.clear()
            time.sleep(DATA_DELAY)


    def connect(self, host='127.0.0.1', port=50000):
        app = self.app
        scene = self.app.scene
        player = self.app.player


        # Generate the pieces (this will change soon)
        print("Generating pieces...")
        t1 = time.time()
        scene.load_jigsaw(PROJECT_FOLDER / 'src' / 'images' / 'sample2.png')
        print(f"Done! {time.time() - t1:.2f}s")


        # Connect to the server
        try:
            self.sock.connect((host, port))
            self.send({'player': {'nick': player.nick}}, forced=True) # Send our nickname
        except ConnectionRefusedError as error:
            print(f"Error connectig to the server: {error}")
            return

        print(f"Connected to server at {host}:{port}")


        # Receive a message that says if the server have pieces or not
        print("Receiving pieces states...")
        do_server_have_pieces = None

        try:
            data = receive(self.sock)

            if data:
                do_server_have_pieces = data.get("do_i_have_pieces")
                print("Done!")

        except (ConnectionResetError, json.JSONDecodeError):
            print(f"Error.\nConnection lost with {host}:{port}")
            return

        if do_server_have_pieces is None:
            print("An error ocurred while connecting to the server. Couldn't retreive pieces state.")
            self.sock.close()
            return


        # If the server doesn't have pieces data yet, then, send mine
        if do_server_have_pieces is False:
            print(f"Sending these pieces... ({len(scene.pieces)} pieces in total)")

            t1 = time.time()

            pieces = [{'id':piece.id, 'pos':piece.pos} for piece in scene.pieces]
            bytes_sent = self.send({'pieces': pieces}, forced=True)

            print(f"Done! ({time.time() - t1}s, {bytes_sent} bytes)")


        # Now, please listen to the server carefully...
        listener_thread = threading.Thread(target=self.listen_carefully, daemon=True)
        listener_thread.start()

        # And, talk to the server politely
        sender_thread = threading.Thread(target=self.data_sender, daemon=True)
        sender_thread.start()

        self.connected = True


    def send(self, data: dict, forced: bool=False):
        if not self.connected and not forced:
            return -1

        return send(self.sock, data)


