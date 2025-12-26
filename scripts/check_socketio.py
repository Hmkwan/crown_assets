#!/usr/bin/env python3
"""Simple Socket.IO smoke-check script used in local dev/CI.
Usage: python scripts/check_socketio.py [--url http://localhost:5020] [--timeout 5]
Exits 0 on successful connect, non-zero on failure.
"""
import sys
import argparse
import socketio

parser = argparse.ArgumentParser()
parser.add_argument('--url', default='http://localhost:5020')
parser.add_argument('--timeout', type=float, default=5.0)
args = parser.parse_args()

# First try a raw WebSocket upgrade (some setups respond to websocket but not to polling)
from websocket import create_connection
try:
    ws = create_connection(args.url.replace('http','ws') + '/socket.io/?EIO=4&transport=websocket')
    print('websocket-upgrade OK')
    ws.close()
    sys.exit(0)
except Exception as e:
    print('websocket upgrade failed, trying socketio client:', e)

s = socketio.Client(logger=False, engineio_logger=False)
try:
    s.connect(args.url, namespaces=['/'])
    print('socketio client connected')
    s.disconnect()
    sys.exit(0)
except Exception as e:
    print('socketio client failed:', e)
    sys.exit(2)
