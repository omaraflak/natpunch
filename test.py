import stun
import logging
from client import Client

logging.basicConfig(level=logging.INFO)

nat_type, external_ip, external_port = stun.get_ip_info(stun_host='stun.l.google.com', stun_port=19302)

logging.info(f'NAT type: {nat_type}')
logging.info(f'Public ip: {external_ip}')
logging.info(f'Public port: {external_port}')

client = Client(external_ip, 8888, 'localhost', 6709, 'dbe6')
sock = client.start()
if sock is not None:
    sock.close()