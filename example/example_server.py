import fire
import logging
from natpunch.server import NatPunchServer


def main(
    host: str = '0.0.0.0',
    port: int = 6709,
    connect_delay: int = 5,
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
    logging.basicConfig(level=levels.get(logging_level, 'info'))
    NatPunchServer(host, port, connect_delay, room_ttl).start()


if __name__ == "__main__":
    fire.Fire(main)
