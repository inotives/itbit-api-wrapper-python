import json
import time
from datetime import datetime

from itbit_api import itBitApi


key = "your-key"
secret = "your-secret"
user_id = "your-userid"

api = itBitApi(key, secret, user_id)
market = 'ETHUSD'


print("PUBLIC API::")
ticker = api.get_ticker(market)
print(">> TICKER -- >>", ticker)
order_book = api.get_order_book(market)
price = (float(order_book["bids"][0][:-1][0])+float(order_book["asks"][0][:-1][0]))/2
print(">> Order Books -- >>", datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "PRICE: %.2f" % price )


print("PRIVATE API::")
wallets = api.get_all_wallets()
print(">> WALLETS -- >>", wallets)