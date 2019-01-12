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


def buy_valbz(exch_mkt, price, index):
    write_to_exchange(exch_mkt, {"type": "add", "order_id": index, "symbol": "VALBZ", "dir": "BUY", "price": price, "size": 5})

def sell_valbz(exch_mkt, price, index):
    write_to_exchange(exch_mkt, {"type": "add", "order_id": index, "symbol": "VALBZ", "dir": "SELL", "price": price, "size": 5})

def buy_vale(exch_mkt, price, index):
    write_to_exchange(exch_mkt, {"type": "add", "order_id": index, "symbol": "VALE", "dir": "BUY", "price": price, "size": 5})

def sell_vale(exch_mkt, price, index):
    write_to_exchange(exch_mkt, {"type": "add", "order_id": index, "symbol": "VALE", "dir": "SELL", "price": price, "size": 5})


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
    id_valbz_buy = 0
    id_valbz_sell = 1

    #3 is VALE
    position_vale = 0
    initialized_vale = False
    id_vale_buy = 3
    id_vale_sell = 4

    position_combined = 0
    #initial setup
    #write_to_exchange(exchange, {"type": "add", "order_id": 10, "symbol": "BOND", "dir": "BUY", "price": 999, "size": 50})
    #write_to_exchange(exchange, {"type": "add", "order_id": 11, "symbol": "BOND", "dir": "SELL", "price": 1001, "size": 50})


    while True:

        message = read_from_exchange(exchange)

        if message['type'] == 'reject': 
            print(message)
            print("\n")

        elif message['type'] == "fill":
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
                sell_valbz(exchange, last_valbz + 1, id_valbz_sell)
                id_valbz_sell += 5

            #filled sell valbz, now buy it
            elif message['order_id'] == 21:
                position_valbz = position_valbz - 1
                position_combined = position_combined - 1
                buy_valbz(exchange, last_valbz - 1, id_valbz_buy)
                id_valbz_buy += 5


            #filled buy vale, now sell it
            elif message['order_id'] == 30:
                position_vale = position_vale + 1
                position_combined = position_combined + 1
                sell_vale(exchange, last_valbz + 5, id_vale_sell)
                id_vale_sell += 5

            #filled sell vale, now buy it
            elif message['order_id'] == 31:
                position_valbz = position_vale - 1
                position_combined = position_combined - 1
                buy_vale(exchange, last_valbz - 5, id_vale_buy)
                if_vale_buy += 5



        elif message['type'] == "trade":
            
            if message["symbol"] == "VALBZ":
                last_valbz = message["price"]
                if not initalized_valbz:

                    initalized_valbz = True

                    sell_valbz(exchange, last_valbz + 2, id_valbz_sell)
                    buy_valbz(exchange, last_valbz - 2, id_valbz_buy)
                    
                    sell_vale(exchange, last_valbz + 5, id_vale_sell)
                    buy_vale(exchange, last_valbz + 5, id_vale_buy)

        elif message['type'] == "close":
            raise Exception("CLOSE!!!")

    



if __name__ == "__main__":
    main()



