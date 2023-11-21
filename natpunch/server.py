import time
import socket
import logging
from typing import Callable
from threading import Thread
from datetime import datetime, timedelta
from natpunch.message import Message, MessageJoin, MessageConnect, MessageTimeout


class NatPunchServer:
    def __init__(self, host: str, port: int, connect_delay: int, room_ttl: int):
        self.host = host
        self.port = port
        self.connect_delay = connect_delay
        self.room_ttl = room_ttl
        self.rooms: dict[str, socket.socket] = dict()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def start(self):
        logging.info(f'Starting server on {self.host}:{self.port}...')
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


    def _handle_client(self, client1: socket.socket):
        try:
            ip1, port1 = client1.getpeername()
            while True:
                message = Message.recv(client1)
                if message.message_id == Message.MESSAGE_JOIN:
                    message_join = MessageJoin.from_message(message)
                    uid = message_join.uid
                    logging.info(f'Client {ip1}:{port1} joined room "{uid}"')
                    if uid in self.rooms:
                        client2 = self.rooms[uid]
                        ip2, port2 = client2.getpeername()
                        del self.rooms[uid]
                        time = int((datetime.now() + timedelta(seconds=self.connect_delay)).timestamp())
                        MessageConnect(ip1, port1, ip2, port2, time).to_message().send(client1)
                        MessageConnect(ip2, port2, ip1, port1, time).to_message().send(client2)
                    else:
                        self.rooms[uid] = client1
                        self._call_later(lambda: self._remove_room_and_notify(uid, client1), self.room_ttl)
        except socket.error as e:
            logging.error(e)
            return
        finally:
            client1.close()


    def _remove_room_and_notify(self, uid: str, sock: socket.socket):
        logging.info(f'Deleting room {uid}...')
        if uid in self.rooms:
            del self.rooms[uid]
            MessageTimeout(uid).to_message().send(sock)


    def _call_later(self, function: Callable[[], None], delay: int):
        def _function():
            time.sleep(delay)
            function()
        Thread(target=_function).start()
