import time
import socket
import random
import logging
from datetime import datetime
from natpunch.message import Message, MessageJoin, MessageConnect


class NatPunchClient:
    def __init__(
        self,
        ip: str,
        port: int,
        room: str | None = None,
        max_attempts: int = 10
    ):
        self.ip = ip
        self.port = port
        self.room = room or random.randbytes(2).hex()
        self.max_attempts = max_attempts

    def start(self) -> socket.socket | None:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            sock.settimeout(120)
            return self._start(sock)
        except socket.error as e:
            logging.error(e)
            return None
        finally:
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()

    def _start(self, sock: socket.socket) -> socket.socket | None:
        logging.info(f'Connecting to natpunch server {self.ip}:{self.port}...')
        sock.connect((self.ip, self.port))
        logging.info(f'Connected!')

        logging.info(f'Joining room "{self.room}"...')
        MessageJoin(self.room).to_message().send(sock)

        logging.info('Waiting for another user...')
        message = Message.recv(sock)
        if message.message_id == Message.MESSAGE_TIMEOUT:
            logging.info('Room closed before another user could join')
            return None

        if message.message_id == Message.MESSAGE_CONNECT:
            logging.info('Another user joined the room!')
            message_connect = MessageConnect.from_message(message)
            now = datetime.now().timestamp()
            if now > message_connect.time:
                logging.info('Could not connect in time')
                return None

            delay = message_connect.time - now
            logging.info(f'Connecting in {int(delay)} seconds...')
            time.sleep(delay)
            return self._nat_punch(message_connect)

    def _nat_punch(self, connect: MessageConnect) -> socket.socket | None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        logging.info(f'Binding socket on port {connect.source_port}')
        sock.bind(('0.0.0.0', connect.source_port))

        ip, port = connect.dest_ip, connect.dest_port
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
