import socket
from dataclasses import dataclass


@dataclass
class Room:
    ip: str
    port: int
    sock: socket.socket
