import stun
import fire
import logging
from typing import Optional
from natpunch.client import Client

def main(
    host: str = '0.0.0.0',
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

    nat_type, external_ip, external_port = stun.get_ip_info(stun_host='stun.l.google.com', stun_port=19302)
    logging.info(f'NAT type: {nat_type}')
    logging.info(f'Public ip: {external_ip}')
    logging.info(f'Public port: {external_port}')

    client = Client(external_ip, external_port, 'localhost', 6709, room)
    sock = client.start()
    if sock is not None:
        logging.info('Peer to peer connection established! Disconnecting...')
        sock.close()


if __name__ == '__main__':
    fire.Fire(main)