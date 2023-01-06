# %%
from cProfile import run
from order_grid import *
from plot_functions import *
from ring_buffer import RingBuffer
from change_leverage_and_margin_type import change_leverage_and_margin
# from order_grid_arithmetic import send_arithmetic_order_grid
from binance.client import Client
from binance.enums import *
from threading import Thread, local
from datetime import datetime


import numpy as np
import pandas_ta as ta
import time
import os
import pandas as pd
import argparse

runs = 0


# %%


parser = argparse.ArgumentParser()
parser.add_argument("-pt", "--paper_trade", type=bool, default=True)
parser.add_argument("-tf", "--timeframe", type=str, default="1h")
parser.add_argument("-ppl", "--price_posision_low", type=float, default=0.0)
parser.add_argument("-pph", "--price_position_high", type=float, default=0.0)

parser.add_argument("-wl", "--window_length", type=int, default=52)
parser.add_argument("-wa", "--atr_window_length", type=int, default=8)
parser.add_argument("-e", nargs="+", help="my help message", type=float,
                        # default=(1.0, 1.146, 1.364, 1.5, 1.618, 1.854, 2.0, 2.146, 2.364)) #1h
                        # default=(1.0, 1.146, 1.364, 1.5, 1.618, 1.854, 2.0, 2.364, 2.5, 2.618)) #15min
                        default=(0.92, 1.16, 1.4, 1.64, 1.88, 2.12, 2.36, 2.6, 2.84)) # 15m (maybe 5min)
                        # default=(0.86, 1.0, 1.146, 1.292, 1.364, 1.5, 1.618, 1.792, 1.854, 2.0)) # 1h (maybe 5min)
parser.add_argument("--max_positions", type=int, default=3)
parser.add_argument("--debug", type=bool, default=False)
parser.add_argument("--momentum", type=bool, default=False)
parser.add_argument("--open_grids", type=bool, default=False)
parser.add_argument("--check_positions_properties", type=bool, default=False)
parser.add_argument("-ag", "--arithmetic_grid", type=bool, default=False)
parser.add_argument("-gs", "--grid_step", type=float, default=0.0)
parser.add_argument("--plot_screened", type=bool, default=False)
parser.add_argument("--run_once", type=bool, default=False)

parser.add_argument("--add_to_ignore", nargs="+", help="my help message", type=str, default=())
parser.add_argument("--run_only_on", nargs="+", help="my help message", type=str, default=())
parser.add_argument("-tp", "--take_profit", type=float, default=0.14)                
parser.add_argument("-sl", "--stop_loss", type=float, default=0.12)                
parser.add_argument("-q", "--quantity", type=float, default=1.1)
parser.add_argument("-lev", "--leverage", type=int, default=17)                


args = parser.parse_args()

api_key = os.environ.get("API_KEY")
api_secret = os.environ.get("API_SECRET")
client = Client(api_key, api_secret)


interval = args.timeframe

window_length = args.window_length
ppl, pph = args.price_posision_low, args.price_position_high
price_position_range = [ppl, pph]
w_atr = args.atr_window_length
pt = args.paper_trade
coefs = np.array(args.e)
debug = args.debug
momentum = args.momentum
open_grids = args.open_grids
arithmetic_grid = args.arithmetic_grid
gs = args.grid_step
plot_screened= args.plot_screened
check_positions_properties = args.check_positions_properties
max_positions = args.max_positions
run_once = args.run_once
add_to_ignore = args.add_to_ignore
run_only_on = list(args.run_only_on)
tp = args.take_profit
sl = args.stop_loss
leverage = args.leverage
qty = args.quantity

# ignore_list = ["MATICUSDT"]
ignore_list = ["AVAXUSDT", "SOLUSDT", "LUNAUSDT", "AAVEUSDT", "HNTUSDT", "YFIUSDT", "MASKUSDT", "IOTXUSDT", "BTCDOMUSDT", "AXSUSDT", "XEMUSDT"]

add_to_ignore = list(add_to_ignore)
print(add_to_ignore)


ignore_list += add_to_ignore

def to_datetime_tz(arg, timedelta=-pd.Timedelta("03:00:00"), unit="ms", **kwargs):
    """
    to_datetime_tz(arg, timedelta=-pd.Timedelta("03:00:00"), unit="ms", **kwargs)

    Args:
        arg (float): epochtime
        timedelta (pd.Timedelta): timezone correction
        unit (string): unit in which `arg` is
        **kwargs: pd.to_datetime remaining kwargs
    Returns:
    pd.Timestamp: a timestamp corrected by the given timedelta
    """
    ts = pd.to_datetime(arg, unit=unit)
    return ts + timedelta


def process_futures_klines(klines):
    # klines = msg["k"]
    klines = pd.DataFrame.from_records(klines, coerce_float=True)
    klines = klines.loc[:, [0, 6, 1, 2, 3, 4, 5]]
    klines.columns = ["init_ts", "end_ts", "open", "high", "low", "close", "volume"]
    # df = pd.DataFrame(klines, columns=["timestamp", "open", "close", "high", "low", "transactionVol","transactionAmt"])
    klines["init_ts"] = klines["init_ts"].apply(to_datetime_tz)
    klines["end_ts"] = klines["end_ts"].apply(to_datetime_tz)
    klines.update(klines.iloc[:, 2:].astype(float))
    return klines

class Cleaner(Thread):
    def __init__(self, client, order_grids):
        Thread.__init__(self)
        self.setDaemon(True)
        self.client = client
        self.spairs = list(order_grids.keys())
        self.positions = {}
        self.order_grids = order_grids
        self.running = True
        self.start()

    def run(self):
        while (len(self.spairs) > 0 and self.running):
            check_positions(self.client, self.spairs, self.positions, self.order_grids)
            time.sleep(1)
    def stop(self):
        self.running = False
        
def check_positions(client, spairs, positions, order_grids):
    for symbol in spairs:
        try:
            last_entry_price = float(positions[symbol]["entryPrice"])
        except KeyError as e:
            print(e)
            last_entry_price = None
        # last_position_amount = float(positions[symbol]["positionAmt"])

        is_closed = False
        symbol_grid = order_grids[symbol]
        position = client.futures_position_information(symbol=symbol)
        positions[symbol] = position[0]
        entry_price = float(position[0]["entryPrice"])
        position_qty = float(position[0]["positionAmt"])
        side = -1 if position_qty < 0 else 1
        position_qty = abs(position_qty)
        # print(json.dumps(position[0], indent=2))
        
        if entry_price == 0.0 and position_qty == 0.0: 

            is_closed = True
        
            try:
                client.futures_cancel_all_open_orders(symbol=symbol)
            except BinanceAPIException as e:
                print(e)
            else:                
                spairs.remove(symbol)
                del positions[symbol]
            # positions.remove(symbol)
        elif entry_price != last_entry_price:
            print(f"""entry price: {entry_price};
                    last entry price: {last_entry_price}
                    difference: {abs(entry_price - last_entry_price) if last_entry_price is not None else None}""")
            print(f"changed tp and sl for {symbol}'s position")
            tp_id = symbol_grid["tp"]["orderId"]
            # sl_id = symbol_grid["sl"]["orderId"]
            try:
                client.futures_cancel_order(symbol=symbol, orderId=tp_id)
                # client.futures_cancel_order(symbol=symbol, orderId=sl_id)
            except BinanceAPIException as e:
                print(e)
                if e.code == -2011:
                    new_tp, new_sl = send_tpsl(client, symbol, tp, None, side, protect=False)
                elif e.code == -2021: #APIError(code=-2021): Order would immediately trigger.
                    pass
                    # new_tp, new_sl = send_tpsl(client, symbol, tp, sl, side, protect=False)
            else:
                new_tp, new_sl = send_tpsl(client, symbol, tp, None, side, protect=False)
                # new_tp, new_sl = send_tpsl(client, symbol, tp, sl, side, protect=False)
                symbol_grid["tp"]["orderId"] = new_tp["orderId"]
                # symbol_grid["sl"]["orderId"] = new_sl["orderId"]
            time.sleep(1.5)

def compute_indicators(klines, coefs=np.array([1.0, 1.364, 1.618, 1.854, 2.0, 2.364, 2.618]), w1=12, w2=26, w3=8, w_atr=8, step=0.0):
    # compute macd
    macd = pd.Series(
        klines["close"].ewm(span=w1, min_periods=w1).mean()
        - klines["close"].ewm(span=w2, min_periods=w2).mean()
    )
    macd_signal = macd.ewm(span=w3, min_periods=w3).mean()
    macd_hist = macd - macd_signal
    # compute atr bands

    atr = ta.atr(klines["high"], klines["low"], klines["close"], length=w_atr)

    sup_grid_coefs = coefs
    inf_grid_coefs = -1.0 * coefs

    hmean = klines.high.ewm(span=w_atr).mean()
    lmean = klines.low.ewm(span=w_atr).mean()
    global_volatility = (((hmean/lmean).mean()-1)*100)
    
    close_ema = klines["close"].ewm(span=w_atr, min_periods=w_atr).mean()
    close_std = klines["close"].ewm(span=w_atr, min_periods=w_atr).std()

    local_volatility = (close_std/close_ema).mean()*100
    

    grid_coefs = np.concatenate((np.sort(inf_grid_coefs), sup_grid_coefs))
    atr_grid = [close_ema + atr * coef for coef in grid_coefs]

    grid_coefs = sup_grid_coefs

    inf_grid = [close_ema - atr * coef for coef in grid_coefs]
    sup_grid = [close_ema + atr * coef for coef in grid_coefs]

    return macd_hist, atr, inf_grid, sup_grid, close_ema, atr_grid, local_volatility, global_volatility


# generating signals
def generate_signal(df, coefs, hist, inf_grid, sup_grid):
    signal = 0
    bands = [0 for _ in coefs]
    for i, (inf_band, sup_band) in enumerate(zip(inf_grid, sup_grid)):
        # print(hist.iloc[-1] > hist.iloc[-2])
        if momentum:
            if (
                df.close.iloc[-1] <= inf_band.iloc[-1]
            ) and (hist.iloc[-1] > hist.iloc[-2]):
                bands[i] = coefs[i]
                signal = 1
            elif (
                df.close.iloc[-1] >= sup_band.iloc[-1]
            ) and (hist.iloc[-1] < hist.iloc[-2]):
                bands[i] = -coefs[i]
                signal = -1
        else:
            if (
                df.close.iloc[-1] <= inf_band.iloc[-1]
            ):
                bands[i] = coefs[i]
                signal = 1
            elif (
                df.close.iloc[-1] >= sup_band.iloc[-1]
            ):
                bands[i] = -coefs[i]
                signal = -1
            
    return signal, bands



def process_all_stats(all_stats):
    perps = [pd.DataFrame.from_records([symbol_data]) for symbol_data in all_stats]
    return perps


# compute price position and check other stuff
def filter_perps(perps, price_position_range=[0.3, 0.7]):
    screened_symbols = []
    price_positions = []
    price_change = []
    daily_volatilities =[]
    for row in perps:
        if "USDT" in row.symbol.iloc[-1] and not ("_" in row.symbol.iloc[-1]) and not ("BTCDOMUSDT" == row.symbol.iloc[-1]):
            # screened_symbols.append(row)
            price_position = (
                float(row.lastPrice.iloc[-1]) - float(row.lowPrice.iloc[-1])
            ) / (float(row.highPrice.iloc[-1]) - float(row.lowPrice.iloc[-1]))
            
            # print(price_position)
            price_positions.append(price_position)  
            row["pricePosition"] = price_position
            row["dailyVolatility"] = (float(row.highPrice.iloc[-1])/float(row.lowPrice.iloc[-1]) - 1)*100
            daily_volatilities.append(row["dailyVolatility"])
            price_change.append(float(row["priceChangePercent"]))
            
            if (
                # price_position <= 0.2 or price_position >= 0.8
                price_position >= price_position_range[0]
                or price_position <= price_position_range[1]
            ):  # and float(row.priceChangePercent.iloc[-1]) >= -2.0:
                # if float(row.priceChangePercent.iloc[-1]) >= -1:
                # print(price_position)
                screened_symbols.append(row)
    print("MARKET SUMMARY:")                
    print(f"avg price position: {sum(np.array(price_positions))/len(price_positions)}")
    print(f"avg daily volatility: {sum(np.array(daily_volatilities))/len(daily_volatilities)}")
    print(f"avg % price change: {sum(np.array(price_change))/len(price_change)}")
    return screened_symbols


def generate_market_signals(symbols, coefs, interval, limit=99, paper=False, positions={}, cpnl={}, update_positions=False):
    # usdt_pairs = [f"{symbol}T" for symbol in symbols.pair]
    signals = {}
    # df = pd.DataFrame.from_dict({})
    df = []
    data = {}
    shown_data = []
    order_grids = {}
    n_positions = 0

    for index, row in symbols.iterrows():

        if n_positions >= max_positions:
            break
        
        symbol = row.symbol
        if symbol in ignore_list:
            continue
        if len(run_only_on) > 0 and symbol not in run_only_on:
            continue
        klines = client.futures_klines(symbol=symbol, interval=interval, limit=limit)
        klines = process_futures_klines(klines)
        data_window = klines.tail(window_length)
        data_window.index = range(len(data_window))
        dw = data_window
        hist, atr, inf_grid, sup_grid, close_ema, atr_grid, local_volatility, global_volatility = compute_indicators(
            dw, coefs, w1=12, w2=26, w3=8, w_atr=w_atr, step=gs
        )

        signal, bands = generate_signal(dw, coefs, hist, inf_grid, sup_grid)
        intensity = sum(bands)/sum(coefs)

        if debug:
            print(f"Screening {symbol}...")
            print(f"bands: {bands}")
            print(f"signal: {signal}")
            print(f"close_ema: {close_ema.iloc[-1]}")
            print(f"atr_grid: {atr_grid.iloc[-1]}")
            print(f"\n")

        data[symbol] = {
            "signals": bands,
            "intensity": intensity,
            "klines": klines,
            "data_window": data_window,
            "hist": hist,
            "atr": atr,
            "inf_grid": inf_grid,
            "sup_grid": sup_grid,
            "close_ema": close_ema,
            "atr_grid": atr_grid,
            "local_volatility": local_volatility,
            "global_volatility": global_volatility,
        }

        if signal != 0:

            print(
            f"""
            ################################################################################
            # {symbol}:
            #   signal: {signal}
            #   bands: {bands}
            #   volatility: {(local_volatility + global_volatility)/2}
            #   local volatiliy: {local_volatility}
            #   global volatiliy: {global_volatility} 
            #################################################################################
            """
            )

            signals[symbol] = bands
            df.append(
                row.filter(
                    items=[
                        "symbol",
                        "priceChangePercent",
                        "lastPrice",
                        "weightedAvgPrice",
                        "pricePosition",
                    ]
                )
            )
            shown_data.append(
                pd.DataFrame(
                    [[symbol, signal, data[symbol]["signals"], data[symbol]["local_volatility"], data[symbol]["global_volatility"]]], 
                    columns = ["symbol", "signal", "bands", "local_volatility", "global_volatility"]
                        )
                    )
            side = signal
            if open_grids:
                # if arithmetic_grid:
                #     send_arithmetic_order_grid(client, symbol, inf_grid, sup_grid, tp, side, qty=qty, protect=False, sl=sl, ag=True, is_positioned=False)
                # else:
                #     send_order_grid(client, symbol, inf_grid, sup_grid, tp, side, qty=qty, protect=False, sl=sl, is_positioned=False)
                res, grid_orders = send_order_grid(client, symbol, inf_grid, sup_grid, tp, side, coefs, qty=qty, protect=False, sl=sl, is_positioned=False)

                if (res == -2019
                    and grid_orders is None):
                        break       

                elif (res == -2019 and
                    grid_orders is not None): #margin not enough to fill the grid

                    print("gridorderstest:", grid_orders["tp"])
                    n_positions += 1
                    order_grids[symbol] = grid_orders
                    break       

                elif res == -4164: #APIError(code=-4164): Order's notional must be no smaller than 5.0 (unless you choose reduce only)
                    order_grids[symbol] = grid_orders
                    n_positions += 1
                    continue
                else:
                    print(grid_orders["tp"])
                    n_positions += 1
                    order_grids[symbol] = grid_orders
                if plot_screened:
                    plot_symboL_atr_grid(symbol, data)
                
            if paper and update_positions:
                if signal > 0:
                    positions[symbol] = [1, sum(np.array(bands) * np.array(inf_grid)[:, -1])/sum(np.array(bands)), 0]
                    # print(positions[symbol])
                elif signal < 0:
                    positions[symbol] = [-1, sum(np.array(bands) * np.array(sup_grid)[:, -1])/sum(np.array(bands)), 0]
                    # print(positions[symbol])
            if paper and not update_positions:

                direction, value, pnl = positions[symbol]

                if direction == 1:
                    if 100*(df[-1].lastPrice - value)/value >= 0.32: #TP/Leverage
                        positions[symbol] = [0, 0, 100*(df[-1].lastPrice - value)/value - 0.08] #close the position, update final pnl
                        cpnl[symbol] += positions[symbol][-1]
                        update_positions = True
                    else:
                        positions[symbol][-1] = 100*(df[-1].lastPrice - value)/value - 0.08 #update pnl

                elif direction == -1:
                    if -100*(value - df[-1].lastPrice)/value  >= 0.32:
                        positions[symbol] = [0, 0, -100*(value - df[-1].lastPrice)/value - 0.08]
                        cpnl[symbol] += positions[symbol][-1]
                        update_positions = True
                    else:
                        positions[symbol][1] = -100*(value - df[-1].lastPrice)/value - 0.08 #update pnl
                    
                    
                # print(symbol, ": ", "signal:", signal, "intensity:", intensity, "bands:", bands)
                # print("positions:", positions[symbol])


        # signals[symbol] = [signal, df]
    return signals, df, data, positions, cpnl, shown_data, order_grids

def prescreen():
    all_stats = client.futures_ticker()
    perps = process_all_stats(all_stats)
    filtered_perps = filter_perps(perps, price_position_range=price_position_range)
    filtered_perps = pd.concat(filtered_perps, axis=0)
    return filtered_perps

def postscreen(filtered_perps, paper=False, positions={}, cpnl={}, update_positions=True):
    signals, rows, data, positions, cpnl, shown_data, order_grids = generate_market_signals(filtered_perps, coefs, interval, limit=99, paper=paper, positions = positions, cpnl=cpnl, update_positions=update_positions)    
    return signals, rows, data, positions, cpnl, shown_data, order_grids

# def updatescreen(filtered_perps, positions, cpnl):
#     signals, rows, data, positions, cpnl, shown_data, order_grids = generate_market_signals(filtered_perps, coefs, interval, limit=99, paper=True, positions = positions, cpnl=cpnl, update_positions=False)    
#     return signals, rows, data, positions, cpnl, shown_data, order_grids

def screen():
    all_stats = client.futures_ticker()
    perps = process_all_stats(all_stats)
    filtered_perps = filter_perps(perps, price_position_range=price_position_range)
    filtered_perps = pd.concat(filtered_perps, axis=0)
    signals, rows, data, positions, shown_data, order_grids = generate_market_signals(filtered_perps, coefs, interval, update_positions=True)
    return signals, rows, data, positions, shown_data, order_grids

def main():
     
    if check_positions_properties:
        try:
            change_leverage_and_margin(leverage=leverage)
        except Exception as e:
            print(e)
    filtered_perps = prescreen()
    # print(filtered_perps)
    
    signals, rows, data, positions, cpnl, shown_data, order_grids = postscreen(filtered_perps, paper=pt, update_positions=True)
    
    if len(rows) > 0:
        sdata = pd.concat(shown_data, axis=0)
        sdf = pd.concat(rows, axis=1).transpose()
        spairs = list(sdf.symbol)

        cleaner = Cleaner(client, order_grids)
        
        # def print_positions(cleaner):
        #     while len(cleaner.spairs) >= 1:
        #         time.sleep(2)
        #         positions_df =pd.DataFrame.from_dict(cleaner.positions, orient='index')
        #         print(f"{len(cleaner.spairs)} positions open")
        #         print(positions_df[["symbol", "positionAmt", "notional", "entryPrice", "markPrice", "unRealizedProfit", "liquidationPrice", "leverage",  "marginType"]])
    
        while len(cleaner.spairs) >= 1:
            time.sleep(3)
            positions_df =pd.DataFrame.from_dict(cleaner.positions, orient='index')
            print(f"{len(cleaner.spairs)} positions open")
            if len(cleaner.spairs) > 0:
                print(positions_df[["symbol", "positionAmt", "notional", "entryPrice", "markPrice", "unRealizedProfit", "liquidationPrice", "leverage",  "marginType"]])
        # printer = Thread(target=print_positions, args=(cleaner,))
        # printer.setDaemon(daemonic=True)
        # printer.start()
        # plot_all_screened(spairs, data)
        # for pair in spairs:
            # print(pair, ": ", data[pair]["atr_grid"])
        # printer.join()
        # print_positions(cleaner)
        
        print("""
        All positions closed.
        Cleaning stuff..."""
        )
        return cleaner
        # print("positions: ", positions)
    else:
        print("Nothing found :( ")  


if __name__ == "__main__":
    data = {}
    runs = 0
    while True:
        ret = main()
        time.sleep(20)
        if ret is not None:
            cleaner = ret
            cleaner.stop()
        if run_once:
            print(f"--run_once: {run_once}; exiting...")
            break
        else:
            runs += 1
        print("Reescreening...")

