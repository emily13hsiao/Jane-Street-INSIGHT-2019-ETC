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
test_mode = True

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


# ~~~~~============== MAIN LOOP ==============~~~~~

"""
My strategy for pricing: 
initialize by?

Every time there's a trade read off what it is and save it as the last fair price.

When submitting a new buy, do fair - 1. When submitting a new sell, do fair + 1.


"""

"""
{"type": "hello", "team": "ASDF"}
{"type": "add", "order_id": N, "symbol": "SYM", "dir": "BUY", "price": N, "size": N}

{"type": "cancel", "order_id": N}


{"type":"trade","symbol":"SYM","price":N,"size":N}
"""

"""
def submit_valbz_vale(num_valbz, num_vale, num_combined):
    if num_combined == 0:
        buy_valbz(last_valbz - 1)
        sell_vale(last_valbz + 10)
    elif num_combined < 0:
"""
def buy_valbz(exch_mkt, price):
    print("buying alasdlkf")
    write_to_exchange(exch_mkt, {"type": "add", "order_id": 20, "symbol": "VALBZ", "dir": "buy", "price": price, "size": 1})

def sell_valbz(exch_mkt, price):
    write_to_exchange(exch_mkt, {"type": "add", "order_id": 21, "symbol": "VALBZ", "dir": "sell", "price": price, "size": 1})

def buy_vale(exch_mkt, price):
    write_to_exchange(exch_mkt, {"type": "add", "order_id": 30, "symbol": "VALE", "dir": "buy", "price": price, "size": 1})

def sell_vale(exch_mkt, price):
    write_to_exchange(exch_mkt, {"type": "add", "order_id": 31, "symbol": "VALE", "dir": "sell", "price": price, "size": 1})


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

    #1: BOND
    fair_bond = 1000

    #2: VALBZ
    last_valbz = 0
    position_valbz = 0
    initalized_valbz = False
    

    #3 is VALE
    position_vale = 0
    initialized_vale = False


    position_combined = 0

    #initial setup
    write_to_exchange(exchange, {"type": "add", "order_id": 10, "symbol": "BOND", "dir": "BUY", "price": 999, "size": 50})
    write_to_exchange(exchange, {"type": "add", "order_id": 11, "symbol": "BOND", "dir": "SELL", "price": 1001, "size": 50})


    while True:

        message = read_from_exchange(exchange)
        if message['type'] == "fill":
            #print("you got a fill: \n")
            #print (message)
            #print("\n")


            #buy bond
            if message['order_id'] == 10:
                number = 50 - message['size']
                write_to_exchange(exchange, {"type": "add", "order_id": 10, "symbol": "BOND", "dir": "BUY", "price": 999, "size": number})

            #sell bond
            elif message['order_id'] == 11:
                number = 50 - message['size']
                write_to_exchange(exchange, {"type": "add", "order_id": 11, "symbol": "BOND", "dir": "SELL", "price": 1001, "size": number})

            #filled buy valbz, now sell it
            elif message['order_id'] == 20:
                position_valbz = position_valbz + 1
                position_combined = position_combined + 1
                sell_valbz(exchange, last_valbz + 1)

            #filled sell valbz, now buy it
            elif message['order_id'] == 21:
                position_valbz = position_valbz - 1
                position_combined = position_combined - 1
                buy_valbz(exchange, last_valbz - 1)


            #filled buy vale, now sell it
            elif message['order_id'] == 30:
                position_vale = position_vale + 1
                position_combined = position_combined + 1
                sell_vale(exchange, last_valbz + 5)

            #filled sell vale, now buy it
            elif message['order_id'] == 31:
                position_valbz = position_vale - 1
                position_combined = position_combined - 1
                buy_vale(exchange, last_valbz - 5)



        elif message['type'] == "trade":
            
            if message["symbol"] == "VALBZ":
                last_valbz = message["price"]
                if not initalized_valbz:
                    initalized_valbz = True

                    write_to_exchange(exchange, {"type": "add", "order_id": 20, "symbol": "VALBZ", "dir": "BUY", "price": last_valbz, "size": 1})
                    sell_valbz(exchange, last_valbz + 1)
                    #buy_valbz(exchange, last_valbz - 1)
                    
                    sell_vale(exchange, last_valbz + 5)
                    buy_vale(exchange, last_valbz + 5)



if __name__ == "__main__":
    main()













