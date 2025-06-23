import fire
import logging
from typing import Optional
from natpunch.client import NatPunchClient

def main(
    ip: str,
    port: int = 6709,
    room: Optional[str] = None,
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
    logging.basicConfig(level=levels.get(logging_level, 'info'))

    client = NatPunchClient(ip, port, room)
    sock = client.start()
    if sock is not None:
        logging.info('Peer to peer connection established! Disconnecting...')
        sock.close()


if __name__ == '__main__':
    fire.Fire(main)