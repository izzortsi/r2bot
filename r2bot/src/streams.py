
# %%

import time

from binance.streams import ThreadedWebsocketManager
from binance.streams import BinanceSocketManager
from auxiliary_functions import api_key, api_secret, client
from src import *
import threading
import time
import pandas_ta as ta

class StreamProcesser:
    def __init__(self, trader):

        self.trader = trader

    def _process_stream_data(self):

        time.sleep(0.1)

        if self.trader.bwsm.is_manager_stopping():
            exit(0)

        data_from_stream_buffer = self.trader.bwsm.pop_stream_data_from_stream_buffer(
            self.trader.stream_name
        )

        if data_from_stream_buffer is False:
            time.sleep(0.01)
            return

        try:
            if data_from_stream_buffer["event_type"] == "kline":

                kline = data_from_stream_buffer["kline"]

                o = float(kline["open_price"])
                h = float(kline["high_price"])
                l = float(kline["low_price"])
                c = float(kline["close_price"])
                v = float(kline["base_volume"])
                #
                # num_trades = int(kline["number_of_trades"])
                # is_closed = bool(kline["is_closed"])

                last_index = self.trader.data_window.index[-1]

                self.trader.now = time.time()
                self.trader.now_time = to_datetime_tz(self.trader.now)
                self.trader.last_price = c

                dohlcv = pd.DataFrame(
                    np.atleast_2d(np.array([self.trader.now_time, o, h, l, c, v])),
                    columns=["date", "open", "high", "low", "close", "volume"],
                    index=[last_index],
                )

                tf_as_seconds = (
                    interval_to_milliseconds(self.trader.strategy.timeframe) * 0.001
                )

                new_close = dohlcv.close
                self.trader.data_window.close.update(new_close)

                # indicators = self.trader.grabber.compute_indicators(
                #     self.trader.data_window.close, **self.trader.strategy.macd_params
                # )
                macd = ta.macd(self.trader.data_window.close)
                # macd = ta.macd(self.trader.data_window.close, **self.trader.strategy.macd_params)
                # print(self.trader.strategy.macd_params)
                hist = macd["MACDh_12_26_9"]
                hist.name = "histogram"
                c = self.trader.data_window.close
                close_ema = c.ewm(span=self.trader.w1).mean()
                close_ema.name = "close_ema"
                close_std = c.ewm(span=self.trader.w1).std()
                close_std.name = "close_std"
                cs = close_ema + self.trader.m1*close_std
                cs.name = "cs"
                ci = close_ema - self.trader.m1*close_std
                ci.name = "ci"
                hist_ema = hist.ewm(span=self.trader.w1).mean()
                hist_ema.name = "hist_ema"
                indicators = pd.concat([c, cs, close_ema, ci, close_std, hist, hist_ema], axis=1)
                date = dohlcv.date

                new_row = pd.concat(
                    [date, indicators.tail(1)],
                    axis=1,
                )

                if (
                    (self.trader.data_window.date.values[-1] - self.trader.data_window.date.values[-2])
                    >= pd.Timedelta(f"{tf_as_seconds / self.trader.manager.rate} seconds")
                ):

                    self.trader.data_window.drop(index=[0], axis=0, inplace=True)
                    self.trader.data_window = self.trader.data_window.append(
                        new_row, ignore_index=True
                    )

                    self.trader.running_candles.append(dohlcv)
                    self.trader.init_time = time.time()
                    
                else:
                    self.trader.data_window.update(new_row)

        except Exception as e:
            self.trader.logger.info(f"{e}")

class StreamProcesser
#%%
def user_ws_callback(msg):
    print(msg["e"])
    # if msg["e"] == "ORDER_TRADE_UPDATE":

    #     order_data = msg["o"]

    #     symbol = order_data["s"]
    #     order_type = order_data["ot"]

    #     order_status = order_data["X"]

    #     # position_amount = order_data["p"]
    #     if (order_status == 'PARTIALLY_FILLED'
    #         or order_status == 'FILLED'):
    #         print(symbol, order_data)
    # elif msg["e"] == "ACCOUNT_UPDATE":
    if msg["e"] == "ACCOUNT_UPDATE":
        if msg["a"]["m"] == "ORDER":
            msg_data = msg["a"]
            positions_data = msg_data["P"]
            for position_data in positions_data:
                print(f"""{position_data["s"]}
                    amount: {position_data["pa"]}
                    entry price: {position_data["ep"]}""")
                position_amount = float(position_data["pa"])
                entry_price = float(position_data["ep"])
                new_pt = 
        else:
            print(msg["a"]["m"])
            # symbol = order_data["s"]
        # symbol = order_data["S"]

# %%
def main():
    twm = ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret)
    twm.start()

    # twm.start_futures_socket(callback=lambda msg: print("twm's got a message:", msg))
    twm.start_futures_socket(callback=user_ws_callback)
    twm.join()


# %%
for wallet in client.futures_account_balance():
    if wallet["asset"] == "USDT":
        usdt_balance = float(wallet["balance"]) 

# %%
usdt_balance
#%%
if __name__ == "__main__":
    main()

# %%
#%%
