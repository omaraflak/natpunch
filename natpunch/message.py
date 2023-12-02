import socket
from dataclasses import dataclass
from natpunch.io import send, recv


@dataclass
class Message:
    MESSAGE_JOIN = 1
    MESSAGE_CONNECT = 2
    MESSAGE_TIMEOUT = 3

    message_id: int
    payload: bytes = b''


    def send(self, sock: socket.socket):
        data = self.message_id.to_bytes(1, 'big') + self.payload
        send(sock, data)


    @classmethod
    def recv(cls, sock: socket.socket) -> 'Message':
        data = recv(sock)
        return Message(data[0], data[1:])


@dataclass
class MessageJoin:
    uid: str


    def to_message(self) -> Message:
        return Message(Message.MESSAGE_JOIN, self.uid.encode())


    @classmethod
    def from_message(cls, message: Message) -> 'MessageJoin':
        return MessageJoin(message.payload.decode())


@dataclass
class MessageConnect:
    source_ip: str
    source_port: int
    dest_ip: str
    dest_port: int
    time: int


    def to_message(self) -> Message:
        payload = ' '.join([
            self.source_ip,
            str(self.source_port),
            self.dest_ip,
            str(self.dest_port),
            str(self.time)
        ]).encode()
        return Message(Message.MESSAGE_CONNECT, payload)


    @classmethod
    def from_message(cls, message: Message) -> 'MessageConnect':
        source_ip, source_port, dest_ip, dest_port, time = message.payload.decode().split(' ')
        return MessageConnect(source_ip, int(source_port), dest_ip, int(dest_port), int(time))


@dataclass
class MessageTimeout:
    uid: str


    def to_message(self) -> Message:
        return Message(Message.MESSAGE_TIMEOUT, self.uid.encode())


    @classmethod
    def from_message(cls, message: Message) -> 'MessageTimeout':
        return MessageTimeout(message.payload.decode())
