#%%


import time
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
import sys
import certifi
import win32api
import os
os.environ['SSL_CERT_FILE'] = certifi.where()
#%%


def message_handler(message):
    print(message)

ws_client = UMFuturesWebsocketClient()
ws_client.start()

ws_client.mini_ticker(
    symbol='bnbusdt',
    id=1,
    callback=message_handler,
)

# Combine selected streams
ws_client.instant_subscribe(
    stream=['bnbusdt@bookTicker', 'ethusdt@bookTicker'],
    callback=message_handler,
)

time.sleep(10)

print("closing ws connection")
ws_client.stop()

# %%
