from itbit_api import itBitApiConnection
import json
import time


userId = 'your-user-id'
client_key = "your-key"
secret_key = "your-secret"


# #create the api connection
itbit_api_conn = itBitApiConnection(clientKey=client_key, secret=secret_key, userId=userId)


# Public ENDPOINT
# TICKERS --------------
ticker = itbit_api_conn.get_ticker('XBTUSD').json()
print ("> PUBLIC :: TICKER -------------------------------- >>")
top_bid = float(ticker['bid'])
top_ask = float(ticker['ask'])

print("PRICE: $", format( ( top_ask + top_bid ) /2, '.2f' ) )
print("GAP: $", format( ( top_ask - top_bid ), '.2f' ) )
print("HIGH-LOW (24H): $", format( float(ticker['high24h']), '.2f'), '-', format( float(ticker['low24h']), '.2f'))
print('TOP BID <> ASK: $', top_bid, "<>", top_ask)
print("VOL24H:", format(float(ticker['volume24h']), '.4f') )



# Private ENDPOINT
# 1. GET ALL WALLETS & Set the WalletID
wallets = itbit_api_conn.get_all_wallets().json()
print ("> BALANCES :: ------------------------------------- >>")
for wallet in wallets:
    print("  > WalletID:", wallet["id"])
    for bal in wallet["balances"]:
        if float(bal["totalBalance"]) == 0: continue
        trading_wallet_id = wallet["id"] if float(bal["totalBalance"]) > 1 else wallets[0]["id"]
        print("   ->", bal["currency"], ":", bal["availableBalance"], '/', bal["totalBalance"])

# 2. Place Order
print('> PLACE, LIST & CANCEL ORDER TEST')
print("  > PLACING NEW ORDER: XBTUSD BUY", )
new_order = itbit_api_conn.create_order(trading_wallet_id, 'buy', 'XBT', '0.0001', '1000', 'XBTUSD').json()
print("   ->",new_order["id"], "(", new_order["status"],") >>", new_order["side"], ":", new_order["amount"], "@", new_order["price"])
time.sleep(1)

print("  > LIST ORDERS ALL OPEN ORDERS: ")
order_status = "open"
print ("ORDER-STATUS::",order_status)
open_orders = itbit_api_conn.get_wallet_orders(trading_wallet_id, {'status':order_status} ).json()
for order in open_orders:
	print(order['id'], "," , order["instrument"] ,",",order['side'], ",", order['amount'], ",", order["price"])

cancel_order_id = new_order["id"]
print("  > CANCELLING ORDER:", cancel_order_id)
cancelled_order = itbit_api_conn.cancel_order(trading_wallet_id, cancel_order_id).json()
print("Cancel Order Submitted -> ", cancelled_order)

# 3. Cancel the Order and List all order cancelled
time.sleep(1)
print("  > LIST ORDERS ALL CANCELLED ORDERS: ")
order_status = "cancelled"
print ("ORDER-STATUS::",order_status)
open_orders = itbit_api_conn.get_wallet_orders(trading_wallet_id, {'status':order_status} ).json()
for order in open_orders:
	print(order['id'], "," , order["instrument"] ,",",order['side'], ",", order['amount'], ",", order["price"])



