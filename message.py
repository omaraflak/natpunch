import json
import socket
from dataclasses import dataclass
from utils import sock_recv, sock_send


@dataclass
class Message:
    MESSAGE_JOIN = 1
    MESSAGE_CONNECT = 2
    MESSAGE_TIMEOUT = 3

    message_id: int
    payload: bytes = b''


    def send(self, sock: socket.socket):
        data = self.message_id.to_bytes(1, 'big') + self.payload
        sock_send(sock, data)


    @classmethod
    def recv(cls, sock: socket.socket) -> 'Message':
        data = sock_recv(sock)
        return Message(data[0], data[1:])


@dataclass
class MessageJoin:
    ip: str
    port: int
    uid: str


    def to_message(self) -> Message:
        payload = f"{self.ip}:{self.port}:{self.uid}".encode()
        return Message(Message.MESSAGE_JOIN, payload)


    @classmethod
    def from_message(cls, message: Message) -> 'MessageJoin':
        ip, port, uid = message.payload.decode().split(':')
        return MessageJoin(ip, int(port), uid)


@dataclass
class MessageConnect:
    ip: str
    port: int
    time: int


    def to_message(self) -> Message:
        payload = f"{self.ip}:{self.port}:{self.time}".encode()
        return Message(Message.MESSAGE_CONNECT, payload)


    @classmethod
    def from_message(cls, message: Message) -> 'MessageConnect':
        ip, port, time = message.payload.decode().split(':')
        return MessageConnect(ip, int(port), int(time))


@dataclass
class MessageTimeout:
    uid: str


    def to_message(self) -> Message:
        return Message(Message.MESSAGE_CONNECT, self.uid.encode())


    @classmethod
    def from_message(cls, message: Message) -> 'MessageTimeout':
        return MessageTimeout(message.payload.decode())
