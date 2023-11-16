import fire
import logging
from natpunch.server import NatPunchServer


def main(
    host: str = '0.0.0.0',
    port: int = 6709,
    connect_delay: int = 10,
    room_ttl: int = 120,
    logging_level: str = 'info'
):
    logging.basicConfig(level=logging._nameToLevel.get(logging_level, 'info'))
    NatPunchServer(host, port, connect_delay, room_ttl).start()


if __name__ == "__main__":
    fire.Fire(main)