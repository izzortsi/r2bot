#%%
from binance.um_futures import UMFutures as Client
from binance.lib.utils import config_logging
from binance.api import ClientError

import argparse
import logging
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import os

# %%
parser = argparse.ArgumentParser(description='Sends a trailing stop order for given parameters.')


parser.add_argument('-s', '--symbol', type= str, help='e.g., btc', default="btc")
parser.add_argument('-tf', '--timeframe', type= str, help='one of: 15m, 1h, 4h, 1d', default="4h")
parser.add_argument('-tp', '--take_profit', type= float, help='take profit, in percentage (should be above 0.1% to cover trading fees)', default=0.5)
parser.add_argument('-ap', '--activation_price', type= float, help='directly uses the given activation price to set the exit point', default=0.0)
parser.add_argument('-sl', '--stop_loss', type= float, help='not implemented yet; ignore', default=0.0)
parser.add_argument('-dwl', '--data_window_length', type= int, help='how many candles to query from binance`s API, up to 500', default=50)
parser.add_argument('-rwl', '--rolling_window_length', type=int, help='lenght of the rolling window to compute means and standard deviations', default=4)
parser.add_argument('-crf', '--callback_rate_factor', type=int, help='to explain', default=10)
parser.add_argument('-d', '--position_direction', type=str, help='position direction: LONG or SHORT', default="LONG")
parser.add_argument('-plt', '--plot_stuff', type=bool, help='plot queried data?', default=False)
parser.add_argument('-so', '--send_orders', type=bool, help='actually send the order?', default=False)

args = parser.parse_args()
#%%
#PARAMETERS


PAIR = (args.symbol + "USDT").upper()
TIMEFRAME = args.timeframe
TAKE_PROFIT = args.take_profit
ACTIVATION_PRICE = args.activation_price
DATA_WINDOW_LENGTH = args.data_window_length
ROLLING_WINDOW_LENGTH = args.rolling_window_length
CALLBACKRATE_FACTOR = args.callback_rate_factor
POSITION_DIRECTION = args.position_direction
PLOT_STUFF = args.plot_stuff
SEND_ORDERS = args.send_orders

if POSITION_DIRECTION == "LONG":
    SIDE = "SELL" 
elif POSITION_DIRECTION == "SHORT":
    SIDE = "BUY"
else:
    raise Exception(f"POSITION_DIRECTION must be either 'LONG' or 'SHORT', and is {POSITION_DIRECTION}")

config_logging(logging, logging.WARNING)

def process_klines(klines):

    df = pd.DataFrame(klines)
    df.columns = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'trades', 'taker_buy_volume', 'taker_buy_quote_asset_volume', 'ignore']
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
    df['open'] = pd.to_numeric(df['open'])
    df['high'] = pd.to_numeric(df['high'])
    df['low'] = pd.to_numeric(df['low'])
    df['close'] = pd.to_numeric(df['close'])
    df['volume'] = pd.to_numeric(df['volume'])
    df['quote_asset_volume'] = pd.to_numeric(df['quote_asset_volume'])
    df['trades'] = pd.to_numeric(df['trades'])
    df['taker_buy_volume'] = pd.to_numeric(df['taker_buy_volume'])
    df['taker_buy_quote_asset_volume'] = pd.to_numeric(df['taker_buy_quote_asset_volume'])
    df['ignore'] = pd.to_numeric(df['ignore'])
    df.drop(['ignore'], axis=1, inplace=True)
    return df

def get_open_positions(positions):
    
    open_positions = {}
    for position in positions:
        if float(position["positionAmt"]) != 0.0:
            open_positions[position['symbol']] = {
                # 'direction': position['positionSide'],
                'entry_price': float(position['entryPrice']),
                'upnl': float(position['unrealizedProfit']), 
                'pos_amt': float(position['positionAmt']),
                'leverage': int(position['leverage']),
                }
            print(f"{open_positions[position['symbol']]}");
    return open_positions

if __name__ == "__main__":

    akey = os.environ.get("API_KEY")
    asec = os.environ.get("API_SECRET")

    futures_client = Client(key = akey, secret= asec)
    
    acc_info = futures_client.account();
    positions = acc_info["positions"];
    open_positions = get_open_positions(positions)
    
    klines = futures_client.continuous_klines(PAIR, 'PERPETUAL', TIMEFRAME, limit=DATA_WINDOW_LENGTH);
    df = process_klines(klines)

    closes_mean = df.close.ewm(halflife=pd.Timedelta(TIMEFRAME)/4, ignore_na=True, min_periods=ROLLING_WINDOW_LENGTH, times=df.open_time).mean()
    closes_std = df.close.ewm(halflife=pd.Timedelta(TIMEFRAME)/4, ignore_na=True, min_periods=ROLLING_WINDOW_LENGTH, times=df.open_time).std()

    avg_pdev = (closes_std/closes_mean).mean() # average percentual deviation from the EMA
    print("avgpdev", avg_pdev)
    callback_rate = max(0.1, round(avg_pdev*100/CALLBACKRATE_FACTOR, ndigits=1)) #the callback rate is a fraction of the percentual stdev
    print("cbr:", callback_rate)
    
    if PLOT_STUFF:
        ax1 = plt.axis(); plt.plot(closes_mean)
        ax2 = plt.axis(); plt.plot(closes_mean + closes_std)
        ax3 = plt.axis(); plt.plot(closes_mean - closes_std)
        plt.show()

    print("upnl", open_positions[PAIR]["upnl"])
    
    entry_price = open_positions[PAIR]["entry_price"];
    leverage = open_positions[PAIR]["leverage"];
    if ACTIVATION_PRICE != 0.0:
        actv_price = ACTIVATION_PRICE
    else:
        actv_price = entry_price*(1+TAKE_PROFIT/(100*leverage))
    print(f"actv_price: {actv_price}")
    quantity = abs(open_positions[PAIR]["pos_amt"])
    print(f"quantity: {quantity}")

    if SEND_ORDERS:
        try:
            response = response = futures_client.new_order(symbol=PAIR, side = SIDE, type= "TRAILING_STOP_MARKET", quantity= quantity, reduceOnly = True, timeInForce="GTC", activationPrice= actv_price, callbackRate=callback_rate)
            # logging.info(response)
        except ClientError as error:
            logging.error(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )
