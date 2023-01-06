
from binance.client import Client
from binance.enums import *
from binance.exceptions import *
import pandas as pd
import time
import os

api_key = os.environ.get("API_KEY")
api_secret = os.environ.get("API_SECRET")
client = Client(api_key, api_secret)

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
    
def get_time_offset(client):
    
    serverTimeSecs = client.get_server_time()["serverTime"]
    localTimeSecs = time.time()*1000
    
    # print(serverTimeSecs) 
    # print(localTimeSecs)
    print("offset:", serverTimeSecs - localTimeSecs)

def get_ping_avg(client, iters):
    
    pingavg = []
    
    for i in range(iters):
        t1 = time.time()
        client.futures_ping()
        t2 = time.time()
        pingavg.append((t2-t1)*1000)
        print((t2-t1)*1000, "ms")
    print("ping average (ms):", sum(pingavg)/len(pingavg))    
    return sum(pingavg)/len(pingavg)

# %%
if __name__ == "__main__":
    get_time_offset(client)
    get_ping_avg(client, 25)
