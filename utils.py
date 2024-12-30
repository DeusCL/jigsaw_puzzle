import json
import socket

def send(sock: socket.socket, data: dict|list) -> int:
    """ Sends a JSON-encoded message over a socket with a 4-byte length prefix. """

    encoded_data = json.dumps(data).encode('utf-8')
    length_prefix = len(encoded_data).to_bytes(4, byteorder='big')
    sock.sendall(length_prefix + encoded_data)
    return len(length_prefix) + len(encoded_data)


def receive(sock: socket.socket) -> dict:
    """ Receives a JSON-encoded message from a socket with a 4-byte length prefix. """

    length_prefix = sock.recv(4)
    if not length_prefix:
        return None
    message_length = int.from_bytes(length_prefix, byteorder='big')

    data = b""
    while len(data) < message_length:
        chunk = sock.recv(message_length - len(data))
        if not chunk:
            raise ConnectionError("Connection closed unexpectedly")
        data += chunk
    
    return json.loads(data.decode('utf-8'))

