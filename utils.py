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


def full_merge(dict1, dict2):
    """
    Recursively updates dict1 with the contents of dict2.
    If a key in dict2 corresponds to a dictionary in dict1, the update is recursive.
    Otherwise, the value from dict2 overwrites the value in dict1.
    """

    for key, value in dict2.items():
        if key in dict1 and isinstance(dict1[key], dict) and isinstance(value, dict):
            # If both values are dictionaries, update recursively
            full_merge(dict1[key], value)
        else:
            # Otherwise, overwrite or add the value
            dict1[key] = value
    return dict1

