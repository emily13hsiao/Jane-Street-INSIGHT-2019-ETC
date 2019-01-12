#!/usr/bin/python

# ~~~~~==============   HOW TO RUN   ==============~~~~~
# 1) Configure things in CONFIGURATION section
# 2) Change permissions: chmod +x bot.py
# 3) Run in loop: while true; do ./bot.py; sleep 1; done

from __future__ import print_function

import sys
import socket
import json

# ~~~~~============== CONFIGURATION  ==============~~~~~
# replace REPLACEME with your team name!
team_name="SPEAROW"
# This variable dictates whether or not the bot is connecting to the prod
# or test exchange. Be careful with this switch!
test_mode = False

# This setting changes which test exchange is connected to.
# 0 is prod-like
# 1 is slower
# 2 is empty
test_exchange_index=0
prod_exchange_hostname="production"

port=25000 + (test_exchange_index if test_mode else 0)
exchange_hostname = "test-exch-" + team_name if test_mode else prod_exchange_hostname

# ~~~~~============== NETWORKING CODE ==============~~~~~
def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((exchange_hostname, port))
    return s.makefile('rw', 1)

def write_to_exchange(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")

def read_from_exchange(exchange):
    return json.loads(exchange.readline())

def buy_valbz(exch_mkt, price, idx):
    write_to_exchange(exch_mkt, {"type": "add", "order_id": idx, "symbol": "VALBZ", "dir": "BUY", "price": price, "size": 1})

def sell_valbz(exch_mkt, price, idx):
    write_to_exchange(exch_mkt, {"type": "add", "order_id": idx, "symbol": "VALBZ", "dir": "SELL", "price": price, "size": 1})

def buy_vale(exch_mkt, price, idx):
    write_to_exchange(exch_mkt, {"type": "add", "order_id": idx, "symbol": "VALE", "dir": "BUY", "price": price, "size": 1})

def sell_vale(exch_mkt, price, idx):
    write_to_exchange(exch_mkt, {"type": "add", "order_id": idx, "symbol": "VALE", "dir": "SELL", "price": price, "size": 1})

"""
When do I want to do conversions?

If vale is currently trading ABOVE fair value
-> I want to sell vale
Sell vale (-)
Buy valbz (+)


If vale is currently trading below fair value
-> I want to buy vale
Buy vale (+)
Sell valbz (-)

"""
def decide_valbz_vale(exchange, valbz_price, vale_price, valbz_id, vale_id):
    if vale_price > valbz_price:
        sell_vale_buy_valbz(exchange, valbz_price, vale_price, valbz_id, vale_id)
    else:
        buy_vale_sell_valbz(exchange, valbz_price, vale_price, valbz_id, vale_id)

def sell_vale_buy_valbz(exchange, valbz_price, vale_price, valbz_id, vale_id):
    #sell vale
    write_to_exchange(exchange, {"type": "add", "order_id": vale_id , "symbol": "VALE", "dir": "SELL", "price": vale_price, "size": 1}) 
    #buy valbz
    write_to_exchange(exchange, {"type": "add", "order_id": valbz_id , "symbol": "VALBZ", "dir": "BUY", "price": valbz_price, "size": 1}) 

def buy_vale_sell_valbz(exchange, valbz_price, vale_price, valbz_id, vale_id):
    #buy vale
    write_to_exchange(exchange, {"type": "add", "order_id": vale_id , "symbol": "VALE", "dir": "BUY", "price": vale_price, "size": 1})
    #sell valbz
    write_to_exchange(exchange, {"type": "add", "order_id": valbz_id , "symbol": "VALBZ", "dir": "SELL", "price": valbz_price, "size": 1})



# ~~~~~============== MAIN LOOP ==============~~~~~

def main():
    exchange = connect()
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    hello_from_exchange = read_from_exchange(exchange)
    # A common mistake people make is to call write_to_exchange() > 1
    # time for every read_from_exchange() response.
    # Since many write messages generate marketdata, this will cause an
    # exponential explosion in pending messages. Please, don't do that!
    print("The exchange replied:", hello_from_exchange, file=sys.stderr)

    print("\n")

    #initial setup
    write_to_exchange(exchange, {"type": "add", "order_id": 10, "symbol": "BOND", "dir": "BUY", "price": 999, "size": 50})
    write_to_exchange(exchange, {"type": "add", "order_id": 11, "symbol": "BOND", "dir": "SELL", "price": 1001, "size": 50})


    #1: BOND
    fair_bond = 1000
    bond_index = 0

    #2: VALBZ
    last_valbz = 0
    valbz_index = 1
    

    #3 is VALE
    last_vale = 0
    vale_index = 2

    while True:

        """~~~REISSUING ORDERS AFTER BOND FILLS~~~"""
        message = read_from_exchange(exchange)

        """~~~UPDATING LATEST MARKET PRICES TO DO VALE AND VALBZ~~~"""
        if message['type'] == 'trade':
            
            if message["symbol"] == "VALBZ":
                last_valbz = message["price"]
            elif message['symbol'] == 'VALE':
                last_vale = message['price']

            if abs(last_valbz - last_vale) > 1:
                decide_valbz_vale(exchange, last_valbz, last_vale, valbz_index, vale_index)
                valbz_index += 3 
                vale_index += 3
        
        elif message['type'] == 'reject': 
            print(message)
            print("\n")

        
        elif message['type'] == "fill":

            #buy bond
            if message['symbol'] == "BOND" and message['dir'] == "BUY":
                number = 50 - message['size']
                write_to_exchange(exchange, {"type": "add", "order_id": bond_index, "symbol": "BOND", "dir": "BUY", "price": 999, "size": number})
                bond_index = bond_index + 3

            #sell bond
            elif message['symbol'] == "BOND" and message['dir'] == "SELL":
                number = 50 - message['size']
                write_to_exchange(exchange, {"type": "add", "order_id": bond_index, "symbol": "BOND", "dir": "SELL", "price": 1001, "size": number})
                bond_index = bond_index + 3

    







if __name__ == "__main__":
    main()

























