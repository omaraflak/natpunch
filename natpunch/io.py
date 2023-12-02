import socket
import select


def send(sock: socket.socket, data: bytes):
    size_bytes = len(data).to_bytes(4, 'big')
    sock.sendall(size_bytes + data)

def recv(sock: socket.socket) -> bytes:
    size = int.from_bytes(_recv_all(sock, 4), 'big')
    return _recv_all(sock, size)


def _recv_all(sock: socket.socket, size: int, max_chunk: int = 1 << 20) -> bytes:
    data = bytearray()
    while len(data) != size:
        if not _has_data(sock):
            continue
        chunk = min(max_chunk, size - len(data))
        received = sock.recv(chunk)
        if received == b'':
            raise socket.error('socket closed!')
        data.extend(received)
    return bytes(data)


def _has_data(sock: socket.socket) -> bool:
    r, _, _ = select.select([sock], [], [])
    return len(r) > 0