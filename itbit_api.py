import json
import time
import requests
try:
    #python3 compatibility
    import urllib.parse as urlparse
except ImportError:
    import urllib as urlparse
import base64
import hashlib
import hmac

import urllib3
urllib3.disable_warnings()



#location of the api (change to https://beta-api.itbit.com/v1 for beta endpoint)
api_address = 'https://api.itbit.com/v1'

class MessageSigner(object):

    def make_message(self, verb, url, body, nonce, timestamp):
        # There should be no spaces after separators
        return json.dumps([verb, url, body, str(nonce), str(timestamp)], separators=(',', ':'))

    def sign_message(self, secret, verb, url, body, nonce, timestamp):
        message = self.make_message(verb, url, body, nonce, timestamp)
        sha256_hash = hashlib.sha256()
        
        nonced_message = str(nonce) + message
        
        sha256_hash.update(nonced_message.encode('utf8'))
        
        hash_digest = sha256_hash.digest()
    
        hmac_digest = hmac.new(secret, url.encode('utf8') + hash_digest, hashlib.sha512).digest()
        return base64.b64encode(hmac_digest)


class itBitApi(object):

    #clientKey, secret, and userId are provided by itBit and are specific to your user account
    def __init__(self, clientKey, secret, userId):
        self.clientKey = clientKey
        self.secret = secret.encode('utf-8')
        self.userId = userId
        self.nonce = 0


    # -------------------------------------------------------------------------------------------------------------------------
    # INTERNAL FUNCTION
    # -------------------------------------------------------------------------------------------------------------------------

    # Make request object
    def make_request(self, verb, url, body_dict):
        url = api_address + url
        nonce = self._get_next_nonce()
        timestamp = self._get_timestamp()
        http = urllib3.PoolManager()

        if verb in ("PUT", "POST"):
            json_body = json.dumps(body_dict)
        else:
            json_body = ""

        signer = MessageSigner()
        signature = signer.sign_message(self.secret, verb, url, json_body, nonce, timestamp)

        auth_headers = {
            'Authorization': self.clientKey + ':' + signature.decode('utf8'),
            'X-Auth-Timestamp': str(timestamp),
            'X-Auth-Nonce': str(nonce),
            'Content-Type': 'application/json'
        }

        try:
            if verb == "GET":
                return json.loads(http.request(verb, url, fields=json_body, headers=auth_headers, timeout=5.0).data.decode('utf-8'))
            elif verb == "POST" or verb == 'PUT':
                return json.loads(http.urlopen(verb, url, headers=auth_headers, body=json_body, timeout=5.0).data.decode("utf-8"))
            else:
                return json.loads(http.request(verb, url, fields=json_body, headers=auth_headers, timeout=5.0).data.decode('utf-8'))
        except Exception as e:
            print("ERROR::", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            print(str(e))

    #increases nonce so each request will have a unique nonce
    def _get_next_nonce(self):
        self.nonce += 1
        return self.nonce

    # Timestamp must be unix time in milliseconds
    def _get_timestamp(self):
        return int(time.time() * 1000)

    # Handling the Query string parameter
    def _generate_query_string(self, filters):
        if filters:
            return '?' + urlparse.urlencode(filters)
        else:
            return ''



    # -------------------------------------------------------------------------------------------------------------------------
    # List of API Function
    # -------------------------------------------------------------------------------------------------------------------------


    # PUBLIC ENDPOINT
    # ----------------

    # GET :: TICKER (https://api.itbit.com/docs#market-data-get-ticker-get)
    # Get exchange tickers information
    def get_ticker(self, tickerSymbol):
        path = "/markets/%s/ticker" % (tickerSymbol)
        response = self.make_request("GET", path, {})
        return response

    # GET :: ORDER_BOOK (https://api.itbit.com/docs#market-data-get-order-book-get) - Order books information
    # Get order books from the exchange
    def get_order_book(self, tickerSymbol):
        path = "/markets/%s/order_book" % (tickerSymbol)
        response = self.make_request("GET", path, {})
        return response


    # PRIVATE ENDPOINT
    # ----------------

    # GET :: ALL WALLETS (https://api.itbit.com/docs#trading-get-all-wallets-get)
    # get all the wallets under user account
    def get_all_wallets(self, filters={}):
        filters['userId'] = self.userId
        queryString = self._generate_query_string(filters)
        path = "/wallets%s" % (queryString)
        response = self.make_request("GET", path, {})
        return response

    # POST :: CREATE WALLET (https://api.itbit.com/docs#trading-new-wallet-post)
    # create a new wallet information
    def create_wallet(self, walletName):
        path = "/wallets"
        response = self.make_request("POST", path, {'userId': self.userId, 'name': walletName})
        return response

    # GET :: WALLET DETAIL (https://api.itbit.com/docs#trading-get-wallet-get)
    # get wallet details
    def get_wallet(self, walletId):
        path = "/wallets/%s" % (walletId)
        response = self.make_request("GET", path, {})
        return response

    # GET :: WALLET DETAIL (https://api.itbit.com/docs#trading-get-wallet-balance-get)
    # Get user balances from the wallet
    def get_wallet_balance(self, walletId, currency):
        path = "/wallets/%s/balances/%s" % (walletId, currency)
        response = self.make_request("GET", path, {})
        return response

    # GET :: WALLET TRADES (https://api.itbit.com/docs#trading-get-trades-get)
    # Get user trades
    def get_wallet_trades(self, walletId, filters={}):
        queryString = self._generate_query_string(filters)
        path = "/wallets/%s/trades%s" % (walletId, queryString)
        print("PATH&PARAMS:", path)
        response = self.make_request("GET", path, {})
        return response


    # GET :: FUNDING HISTORY (https://api.itbit.com/docs#trading-get-funding-history-get)
    # returns a list of funding history for a wallet, response will be paginated and limited to 50 items per response
    def get_funding_history(self, walletId, filters={}):
        queryString = self._generate_query_string(filters)
        path = "/wallets/%s/funding_history%s" % (walletId, queryString)
        response = self.make_request("GET", path, {})
        return response


    # GET :: ORDERS (https://api.itbit.com/docs#trading-get-orders-get)
    # returns a list of orders for a wallet
    # response will be paginated and limited to 50 items per response
    # orders can be filtered by status (ex: open, filled, etc)
    def get_wallet_orders(self, walletId, filters={}):
        queryString = self._generate_query_string(filters)
        path = "/wallets/%s/orders%s" % (walletId, queryString)
        response = self.make_request("GET", path, {})
        return response

    # POST :: CREATE NEW ORDER (https://api.itbit.com/docs#trading-new-order-post)
    # creates a new limit order
    def create_order(self, walletId, side, currency, amount, price, instrument):
        path = "/wallets/%s/orders/" % (walletId)
        response = self.make_request("POST", path, {'type': 'limit', 'currency': currency, 'side': side, 'amount': amount, 'price': price, 'instrument': instrument})
        return response

    # POST :: CREATE NEW ORDER WITH CUSTOM DISPLAY (https://api.itbit.com/docs#trading-new-order-post)
    #creates a new limit order
    def create_order_with_display(self, walletId, side, currency, amount, price, display ,instrument):
        path = "/wallets/%s/orders/" % (walletId)
        response = self.make_request("POST", path, {'type': 'limit', 'currency': currency, 'side': side, 'amount': amount, 'price': price, 'display': display, 'instrument': instrument})
        return response

    # GET :: ORDER DETAIL (https://api.itbit.com/docs#trading-get-order-get)
    #returns a specific order by order id
    def get_order(self, walletId, orderId):
        path = "/wallets/%s/orders/%s" % (walletId, orderId)
        response = self.make_request("GET", path, {})
        return response

    # DELETE :: CANCEL ORDER (https://api.itbit.com/docs#trading-cancel-order-delete)
    # cancels an order by order id
    def cancel_order(self, walletId, orderId):
        path = "/wallets/%s/orders/%s" % (walletId, orderId)
        response = self.make_request("DELETE", path, {})
        return response

    # POST :: WALLET FUNDS TRANSFER (https://api.itbit.com/docs#trading-new-wallet-transfer-post)
    #transfers funds of a single currency between two wallets
    def create_wallet_transfer(self, sourceWalletId, destinationWalletId, amount, currencyCode):
        path = "/wallet_transfers"
        response = self.make_request("POST", path, {'sourceWalletId': sourceWalletId, 'destinationWalletId': destinationWalletId, 'amount': amount, 'currencyCode': currencyCode})
        return response

    # POST :: CRYPTO DEPOSIT () // !!!! DISABLED ON ITBIT ENDPOINT AT THE MOMENT !!!!
    #returns a new bitcoin address for deposits to a wallet
    def cryptocurrency_deposit_request(self, walletId, currency):
        path = "/wallets/%s/cryptocurrency_deposits" % (walletId)
        response = self.make_request("POST", path, {'currency': currency})
        return response

    # POST :: CRYPTO WItHDRAWAL () // !!!! DISABLED ON ITBIT ENDPOINT AT THE MOMENT !!!!
    # requests a withdrawal to a bitcoin address
    def cryptocurrency_withdrawal_request(self, walletId, currency, amount, address):
        path = "/wallets/%s/cryptocurrency_withdrawals" % (walletId)
        response = self.make_request("POST", path, {'currency': currency, 'amount': amount, 'address': address})
        return response
