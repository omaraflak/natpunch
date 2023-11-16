import stun
import fire
import logging
from typing import Optional
from natpunch.client import NatPunchClient

def main(
    ip: str,
    port: int = 6709,
    source_ip: Optional[str] = None,
    source_port: Optional[int] = None,
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

    if not source_ip or not source_port:
        nat_type, source_ip, source_port = stun.get_ip_info(stun_host='stun.l.google.com', stun_port=19302)
        logging.info(f'NAT type: {nat_type}')
        logging.info(f'Public ip: {source_ip}')
        logging.info(f'Public port: {source_port}')

    client = NatPunchClient(ip, port, source_ip, source_port, room)
    sock = client.start()
    if sock is not None:
        logging.info('Peer to peer connection established! Disconnecting...')
        sock.close()


if __name__ == '__main__':
    fire.Fire(main)