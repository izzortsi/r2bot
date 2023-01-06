
from binance.client import Client
from binance.enums import *
from binance.exceptions import *
import time
import os

api_key = os.environ.get("API_KEY")
api_secret = os.environ.get("API_SECRET")
client = Client(api_key, api_secret)


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
