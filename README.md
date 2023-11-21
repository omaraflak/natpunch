# NAT Punch

A server/client tool to coordinate NAT hole punching in order to establish peer-to-peer socket connections.

# Explanation

NAT Traversal (or NAT hole punching) allows you to create peer to peer connections without port forwarding on any of the clients. The technique relies on the fact that the NAT will open a port temporarily to receive responses to outgoing requests (e.g. when you browse the web).

If two clients can connect to each others' public IP address on the port allocated by the NAT for an outgoing connection, then we can trick the NAT into thinking that the incoming socket connection is the response of the outgoing connection to the peer, thus resulting in a TCP session.

To do this successfully, both clients need to connect at the same time on the correct address and port.

This client/server app facilitates the process of sharing public ip/port and coordinates the connections. The server hosts "rooms" which can hold 2 peers. When two peers join a room, they will get each others addresses and a time to connect in sync.

## Server

```
python example_server.py
```

## Client

```
python example_client.py --ip=<server ip> --port=<server port> [--room=<id>]
```

`--room` parameter should be a unique string that identifies the room to join. If not specified, it will be generated automatically.
