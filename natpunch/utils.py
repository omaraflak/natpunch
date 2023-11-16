import socket


def sock_send(sock: socket.socket, data: bytes):
    sock.sendall(len(data).to_bytes(4, 'big') + data)


def sock_recv(sock: socket.socket) -> bytes:
    size_bytes = _recv_all(sock, 4)
    size = int.from_bytes(size_bytes, 'big')
    return _recv_all(sock, size)


def _recv_all(sock: socket.socket, size: int) -> bytes:
    data = bytearray()
    while len(data) != size:
        received = sock.recv(size - len(data))
        if received == b'':
            raise socket.error('socket closed!')
        data.extend(received)
    return bytes(data)
