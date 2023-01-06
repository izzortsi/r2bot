
# %%
# %matplotlib qt
import matplotlib.pyplot as plt
import numpy as np
import time
import logging
from binance.lib.utils import config_logging
import time

from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient as FuturesWebsocketClient
import pandas as pd
import pandas_ta as ta

config_logging(logging, logging.DEBUG)
import sys
import certifi
import win32api
import os
os.environ['SSL_CERT_FILE'] = certifi.where()
# %%

class RingBuffer(FuturesWebsocketClient):
    def __init__(self, size):
        super().__init__()
        self.df = pd.DataFrame()
        self.size = size
        self.indicators = pd.DataFrame()
        

    def message_handler(self, message):
        try:
            # print(message)
            # print(type(message))
            if (message["e"] == "continuous_kline") and (len(self.df) < self.size):
                kline = message["k"]
                self.df = pd.concat([
                        self.df, 
                        pd.DataFrame([   
                            {
                            "s": message["ps"],
                            "date": pd.to_datetime(message["E"], unit="ms"),
                            "o": pd.to_numeric(kline["o"]),
                            "h": pd.to_numeric(kline["h"]),
                            "l": pd.to_numeric(kline["l"]),
                            "c": pd.to_numeric(kline["c"]),
                            "v": pd.to_numeric(kline["v"]),
                            },
                            ])], 
                            ignore_index = True,
                        )
            elif (message["e"] == "continuous_kline") and (len(self.df) >= self.size):
                kline = message["k"]
                self.df.drop(axis=0, index = 0, inplace=True), 
                self.df = pd.concat([
                        self.df, 
                        pd.DataFrame([   
                            {
                            "s": message["ps"],
                            "date": pd.to_datetime(message["E"], unit="ms"),
                            "o": pd.to_numeric(kline["o"]),
                            "h": pd.to_numeric(kline["h"]),
                            "l": pd.to_numeric(kline["l"]),
                            "c": pd.to_numeric(kline["c"]),
                            "v": pd.to_numeric(kline["v"]),
                            },
                            ])], 
                            ignore_index = True,
                        )
                atr_ = ta.atr(self.df.h, self.df.l, self.df.c, length=7)                        

                closes_ema = ta.ema(self.df.c, length=7)
                closes_ema.name = "ema"

                sup_band = closes_ema + 1.618*atr_
                sup_band.name = "sband"

                inf_band = closes_ema - 1.618*atr_
                inf_band.name = "iband"

                self.indicators = pd.concat([inf_band, closes_ema, sup_band], axis=1)
                # print(self.df.iloc[-1], "\n", self.indicators.iloc[-1])

        except Exception as e:
            print(e)

b = RingBuffer(64)
b.start()
b.continuous_kline(
    pair="btcusdt",
    id=1,
    contractType="perpetual", 
    interval='1m',
    callback=b.message_handler,
)

# %%
len(b.indicators)
# %%

#%%
if len(b.indicators) == b.size:
    f, ax = plt.subplots(figsize=(12, 8))

    ax.plot(b.df.date, b.df.c, label="close")
    # ax.plot(b.df.date, b.indicators.ema)
    ax.plot(b.df.date, b.indicators.iband)
    ax.plot(b.df.date, b.indicators.sband)
# %%
ax.clear()
# %%

# ax.lines[0].set_data(b.df.date, b.df.c)
# ax.lines[0].set_data(b.df.date, b.indicators.ema)
# ax.lines[2].set_data(b.df.date, b.indicators.iband)
# ax.lines[3].set_data(b.df.date, b.indicators.sband)
# #%%

# #%%
# ax.lines[0].draw(ax.plot(b.df.date, b.df.c))
# ax.lines[1].draw(ax.plot(b.df.date,b.indicators.ema))
# ax.lines[2].draw(ax.plot(b.df.date,b.indicators.iband))
# ax.lines[3].draw(ax.plot(b.df.date,b.indicators.sband))
#%%
# %matplotlib qt
# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.animation import FuncAnimation

# fig, ax = plt.subplots()
# xdata, ydata = [], []
# ln, = plt.plot([], [], 'ro')

# def init():
#     ax.set_xlim(0, 2*np.pi)
#     ax.set_ylim(-1, 1)
#     return ln,

# def update(frame):
#     xdata.append(frame.index[-1])
#     ydata.append(frame.c.iloc[-1])
#     ln.set_data(xdata, ydata)
#     return ln,

# ani = FuncAnimation(fig, update, frames=b.df,
#                     init_func=init, blit=True)
# plt.show()
# %%
%matplotlib qt
import matplotlib.pyplot as plt
from drawnow import drawnow
from time import sleep

def make_fig():
    plt.plot(b.df.date, b.df.c)  # I think you meant this
    plt.plot(b.df.date, b.df.h)  # I think you meant this
    plt.plot(b.df.date, b.df.l)  # I think you meant this

plt.ion()  # enable interactivity
fig = plt.figure()  # make a figure

x = list()
y_1 = list()
y_2 = list()
y_3 = list()
i = 0 
while b.is_alive():
    if not (len(b.indicators) == b.size):
        sleep(0.5)
        x.append(b.df.date.iloc[-1])
        y_1.append(b.df.c.iloc[-1])  # or any arbitrary update to your figure's data
        y_2.append(b.df.h.iloc[-1])  # or any arbitrary update to your figure's data
        y_3.append(b.df.l.iloc[-1])  # or any arbitrary update to your figure's data
        i += 1
        drawnow(make_fig)
    elif len(b.indicators) == b.size:
        def make_fig():
            plt.plot(b.df.date, b.df.c)  # I think you meant this
            plt.plot(b.df.date, b.indicators.iband)  # I think you meant this
            plt.plot(b.df.date, b.indicators.sband)  # I think you meant this        
        sleep(0.5)
        x.append(b.df.date.iloc[-1])
        y_1.append(b.df.c.iloc[-1])  # or any arbitrary update to your figure's data
        y_2.append(b.indicators.iband[-1])  # or any arbitrary update to your figure's data
        y_3.append(b.indicators.sband[-1])  # or any arbitrary update to your figure's data
        i += 1
        drawnow(make_fig)

# %%
