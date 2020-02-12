# p2p-chat
Python implementation of P2P chat with local chat history

## To run
#### Install External dependencies
```
pip3 install -r requirements
```
#### Start chat instance
```
python3 chat.py
```

## Schematic

### Threads for P2P chat:
- receiving_thread: To receive messages sent by other devices in network
- send_thread: To broadcast messages to other devices in network.
- broadcast_online_status_thread: To broadcast 'alive' messages to other devices in network.

#### Features
- Local chat history
- Any number of users supported
- Only takes up one socket port of the device
- Each host knows about the alive devices in the network
