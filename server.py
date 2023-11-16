import fire
import time
import socket
import logging
from typing import Callable
from threading import Thread
from datetime import datetime, timedelta

from room import Room
from message import Message, MessageJoin, MessageConnect, MessageTimeout


class Server:
    def __init__(self, host: str, port: int, connect_delay: int, room_ttl: int):
        self.host = host
        self.port = port
        self.connect_delay = connect_delay
        self.room_ttl = room_ttl
        self.rooms: dict[str, Room] = dict()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def start(self):
        logging.info(f'Start server on {self.host}:{self.port}...')
        self.server.bind((self.host, self.port))
        self.server.listen()
        self._accept_clients()
        self.server.close()


    def _accept_clients(self):
        try:
            while True:
                client, address = self.server.accept()
                logging.info(f'Client connected: {address[0]}:{address[1]}')
                Thread(target=self._handle_client, args=(client,)).start()
        except socket.error as e:
            logging.error(e)


    def _handle_client(self, client: socket):
        try:
            while True:
                message = Message.recv(client)
                if message.message_id == Message.MESSAGE_JOIN:
                    message_join = MessageJoin.from_message(message)
                    uid = message_join.uid
                    logging.info(f'Client {message_join.ip}:{message_join.port} wants to join room {uid}')
                    if uid in self.rooms:
                        room = self.rooms[uid]
                        del self.rooms[uid]
                        time = int((datetime.now() + timedelta(seconds=self.connect_delay)).timestamp())
                        MessageConnect(room.ip, room.port, time).to_message().send(client)
                        MessageConnect(message_join.ip, message_join.port, time).to_message().send(room.sock)
                    else:
                        self.rooms[uid] = Room(message_join.ip, message_join.port, client)
                        self._call_later(lambda: self._remove_room_and_notify(uid, client), self.room_ttl)
        except socket.error as e:
            logging.error(e)
            return
        finally:
            client.close()


    def _remove_room_and_notify(self, uid: str, sock: socket.socket):
        logging.info(f'Deleting room {uid}...')
        if uid not in self.rooms:
            return
        del self.rooms[uid]
        MessageTimeout(uid).to_message().send(sock)


    def _call_later(self, function: Callable[[], None], delay: int):
        def _function():
            time.sleep(delay)
            function()
        Thread(target=_function).start()


def main(
    host: str = '0.0.0.0',
    port: int = 6709,
    connect_delay: int = 15,
    room_ttl: int = 120,
    logging_level: str = 'info'
):
    levels = {
        'critical': logging.CRITICAL,
        'error': logging.ERROR,
        'warn': logging.WARNING,
        'warning': logging.WARNING,
        'info': logging.INFO,
        'debug': logging.DEBUG
    }
    logging.basicConfig(level=levels.get(logging_level, 'error'))
    Server(host, port, connect_delay, room_ttl).start()


if __name__ == "__main__":
    fire.Fire(main)