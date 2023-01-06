
# %%

import json
from binance.um_futures import UMFutures as Client
import os

# %%

akey = os.environ.get("API_KEY")
asec = os.environ.get("API_SECRET")
client = Client(akey, asec)
ex_info = client.exchange_info()

# %%
ex_info
# %%
with open("exchangeInfo.json", "w") as json_file:
    json.dump(ex_info, json_file, indent=4)
# %%
with open("exchangeInfo.json") as f:
    data = json.load(f)

# %%
symbols_dict = {}
symbols_filters = {}

# %%
data["symbols"][0]["filters"][0]
# %%

for symbol_data in data["symbols"]:
    if symbol_data["contractType"] == "PERPETUAL" and (
        symbol_data["quoteAsset"] == "USDT"): #or symbol_data["quoteAsset"] == "BUSD"):

        symbol = symbol_data["symbol"]
        symbols_dict[symbol] = symbol_data
        # ticksize = len(str(float(symbol_data["filters"][0]["tickSize"])).split(".")[-1])
        filters = symbol_data["filters"]
        
        tickSize = filters[0]["tickSize"]
        stepSize = filters[1]["stepSize"]
        minQty = filters[1]["minQty"]
        
        marketStepSize = filters[2]["stepSize"]
        marketMinQty = filters[2]["minQty"]
        


        symbols_filters[symbol] = {
            "pricePrecision": symbol_data["pricePrecision"],
            "quantityPrecision": symbol_data["quantityPrecision"],
            "tickSize": tickSize,
            "stepSize": stepSize,
            "minQty": minQty,	
        }


# %%
len(symbols_dict)
len(data["symbols"])

# %%
with open("symbols_data.json", "w") as json_file:
    json.dump(symbols_dict, json_file, indent=4)


# %%

with open("symbols_filters.json", "w") as json_file:
    json.dump(symbols_filters, json_file, indent=4)

#%%
