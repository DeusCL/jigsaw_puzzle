import socket
import threading
import json
import time
import random

from config import DATA_CHUNK_SIZE, DATA_DELAY
from utils import send, receive, full_merge


class Server:
    def __init__(self, host='127.0.0.1', port=50000):
        self.sock = self.init_socket(host, port)

        # This dictionary contains the pieces and its positions along the map.
        # When a client connects, the server will send this data.
        # If the client receives an empty dict, then, the client will generate
        # this pieces and will send the data of all pieces to this server.
        self.pieces = {}


        # A dictionary containing the data of the players, this dict will contain
        # the address as the key, and, as the value, will contain the player data.
        # The player data is: {'sock', 'nick', 'mpos', 'piece'}
        # where 'mpos' and 'piece' are the cursor position and the piece grabbed, respectively.
        self.players = {}


    def init_socket(self, host: str, port: int) -> socket.socket:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))

        return server_socket
    

    def update_piece(self, piece_data: dict):
        self.pieces.update({piece_data['id']: piece_data['pos']})


    def process_message(self, message: dict, client_socket: socket.socket, client_address: tuple[str, int]):
        if not message:
            return

        str_address = self.format_address(client_address)


        if "pieces" in message:
            # Update a bunch of pieces
            incoming_pieces_data = message.get("pieces")
            print(f"Updating {len(incoming_pieces_data)} pieces at once...")
            for piece_data in incoming_pieces_data:
                self.update_piece(piece_data)


        if "player" in message:
            # Update a player
            player_data = self.players[str_address]
            incoming_player_data = message.get("player")

            if not "nick" in player_data.keys() and "nick" in incoming_player_data.keys():
                print(f"{incoming_player_data.get('nick')} joined the game")

            if "piece" in incoming_player_data.keys():
                piece = incoming_player_data.get("piece")

                piece_id = piece.get("id")
                piece_pos = piece.get("pos")

                if not (piece_id and piece_pos):
                    return

                self.update_piece(piece)

            full_merge(player_data, incoming_player_data)


    def format_address(self, address: tuple[str, int]) -> str:
        """ Returns a formated address """
        ip, port = address
        return f"{ip}:{port}"


    def handle_client(self, client_socket: socket.socket, client_address: tuple[str, int]):
        str_address = self.format_address(client_address)

        print(f"Client connected: {str_address}")


        # Send the pieces to the client
        if len(self.pieces) > 0:
            # Saying to the client that I DO have the pieces
            send(client_socket, {"do_i_have_pieces": True})

            # Now, send the pieces I have
            pieces = [{'id':piece_id, 'pos':piece_pos} for piece_id, piece_pos in self.pieces.items()]
            send(client_socket, {"pieces": pieces})

        else:
            # Saying to the client that I DON'T have the pieces yet, please send me the pieces you have
            send(client_socket, {"do_i_have_pieces": False})


        # This player must be added after having sent the pieces data to prevent conflict with self.data_sender
        self.players[str_address] = {'sock':client_socket}


        while True:
            try:
                data = receive(client_socket)

                try:
                    self.process_message(data, client_socket, client_address)
                except Exception as error:
                    print(f"Error processing the message: {error}")

            except (ConnectionResetError, ConnectionError, json.JSONDecodeError):
                print(f"Connection lost with {client_address}")
                break

        client_socket.close()


    def data_sender(self):
        while True:
            if len(self.players) < 2:
                time.sleep(DATA_DELAY)
                continue

            for player_address, player_data in self.players.items():
                client_sock = player_data.get("sock")

                other_players = []

                for foreign_address, foreign_data in self.players.items():
                    if foreign_address == player_address:
                        continue

                    data_to_send = {'address': foreign_address, **{key: value for key, value in foreign_data.items() if key != 'sock'}}

                    if "piece" in foreign_data.keys():
                        del foreign_data['piece']

                    other_players.append(data_to_send)

                send(client_sock, {'players': other_players})

            time.sleep(DATA_DELAY)


    def start(self):
        self.sock.listen(5)
        host, port = self.sock.getsockname()
        print(f"Server listening on {host}:{port}")

        print("Initializing data sender in another thread...")
        sender_thread = threading.Thread(target=self.data_sender)
        sender_thread.start()

        while True:
            client_socket, client_address = self.sock.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
            client_thread.start()



if __name__ == "__main__":
    server_ip = input("Enter ip: ")
    server_port = int(input("Enter port: "))
    server = Server(host=server_ip, port=server_port)
    server.start()

