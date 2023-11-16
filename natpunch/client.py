import time
import socket
import random
import logging
from typing import Optional
from datetime import datetime
from natpunch.message import Message, MessageJoin, MessageConnect


class NatPunchClient:
    def __init__(
        self,
        server_ip: str,
        server_port: int,
        source_ip: str,
        source_port: int,
        room: Optional[str] = None,
        max_attempts: int = 10
    ):
        self.source_ip = source_ip
        self.source_port = source_port
        self.server_ip = server_ip
        self.server_port = server_port
        self.room = room or random.randbytes(2).hex()
        self.max_attempts = max_attempts


    def start(self) -> Optional[socket.socket]:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            return self._start(sock)
        except socket.error as e:
            logging.error(e)
            return None
        finally:
            sock.close()


    def _start(self, sock: socket.socket) -> Optional[socket.socket]:
        logging.info(f'Connecting to {self.server_ip}:{self.server_port}...')
        sock.connect((self.server_ip, self.server_port))
        logging.info(f'Connected!')

        logging.info(f'Joining room "{self.room}"...')
        MessageJoin(self.source_ip, self.source_port, self.room).to_message().send(sock)

        logging.info(f'Waiting for another user...')
        message = Message.recv(sock)
        if message.message_id == Message.MESSAGE_TIMEOUT:
            logging.info('Room closed before another user could join')
            return None

        if message.message_id == Message.MESSAGE_CONNECT:
            logging.info('Another user joined the room!')
            message_connect = MessageConnect.from_message(message)
            now = int(datetime.now().timestamp())
            if now > message_connect.time:
                logging.info('Could not connect in time')
                return None
            
            delay = message_connect.time - now
            logging.info(f'Connecting in {delay} seconds...')
            time.sleep(delay)
            socket.close()
            return self._nat_punch(message_connect.ip, message_connect.port)
            

    def _nat_punch(self, ip: str, port: int) -> Optional[socket.socket]:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        logging.info(f'Binding socket on {self.source_ip}:{self.source_port}...')
        sock.bind(('0.0.0.0', self.source_port))

        logging.info(f'Initiate NAT punching on {ip}:{port}...')
        sock.settimeout(30)
        for _ in range(self.max_attempts):
            try:
                sock.connect((ip, port))
                logging.info('NAT hole punching succeeded! Client connected.')
                return sock
            except socket.error as e:
                logging.error(f'Could not connect to {ip}:{port}: {e}')
        
        sock.close()
        return None
