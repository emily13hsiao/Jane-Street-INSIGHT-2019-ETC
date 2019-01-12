#!/usr/bin/python

# ~~~~~==============   HOW TO RUN   ==============~~~~~
# 1) Configure things in CONFIGURATION section
# 2) Change permissions: chmod +x bot.py
# 3) Run in loop: while true; do ./bot.py; sleep 1; done

from __future__ import print_function

import sys
import socket
import json
import time
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


def buy_valbz(exch_mkt, price, idx):
    write_to_exchange(exch_mkt, {"type": "add", "order_id": idx, "symbol": "VALBZ", "dir": "BUY", "price": price, "size": 1})

def sell_valbz(exch_mkt, price, idx):
    write_to_exchange(exch_mkt, {"type": "add", "order_id": idx, "symbol": "VALBZ", "dir": "SELL", "price": price, "size": 1})

def buy_vale(exch_mkt, price, idx):
    write_to_exchange(exch_mkt, {"type": "add", "order_id": idx, "symbol": "VALE", "dir": "BUY", "price": price, "size": 1})

def sell_vale(exch_mkt, price, idx):
    write_to_exchange(exch_mkt, {"type": "add", "order_id": idx, "symbol": "VALE", "dir": "SELL", "price": price, "size": 1})


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

    pnl = 0

    #1: BOND
    fair_bond = 1000

    #2: VALBZ
    last_valbz = 0
    my_valbz_sell_price = 0
    my_valbz_buy_price = 0
    position_valbz = 0
    initalized_valbz = False
    spread_valbz = 0
    id_valbz_buy = 0
    id_valbz_sell = 1
    

    #3 is VALE
    position_vale = 0
    my_vale_sell_price = 0
    my_vale_buy_price = 0
    initialized_vale = False
    spread_vale = 0
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
            if message['symbol'] == "BOND" and message['dir'] == "BUY":
                number = 50 - message['size']
                write_to_exchange(exchange, {"type": "add", "order_id": 10, "symbol": "BOND", "dir": "BUY", "price": 999, "size": number})

            #sell bond
            if message['symbol'] == "BOND" and message['dir'] == "SELL":
                number = 50 - message['size']
                write_to_exchange(exchange, {"type": "add", "order_id": 11, "symbol": "BOND", "dir": "SELL", "price": 1001, "size": number})

            #filled buy valbz, now sell it
            elif message['symbol'] == 'VALBZ' and message['dir'] == 'SELL':
                position_valbz = position_valbz + 1
                position_combined = position_combined + 1
                sell_valbz(exchange, last_valbz + 1, id_valbz_sell)
                my_valbz_sell_price = last_valbz + 1
                id_valbz_sell += 5

            #filled sell valbz, now buy it
            elif message['order_id'] == 21:
                position_valbz = position_valbz - 1
                position_combined = position_combined - 1
                buy_valbz(exchange, last_valbz - 1, id_valbz_buy)
                my_valbz_buy_price = last_valbz - 1
                id_valbz_buy += 5


            #filled buy vale, now sell it
            elif message['order_id'] == 30:
                position_vale = position_vale + 1
                position_combined = position_combined + 1
                sell_vale(exchange, last_valbz + 5, id_vale_sell)
                my_vale_sell_price = last_valbz + 5
                id_vale_sell += 5

            #filled sell vale, now buy it
            elif message['order_id'] == 31:
                position_valbz = position_vale - 1
                position_combined = position_combined - 1
                buy_vale(exchange, last_valbz - 5, id_vale_buy)
                my_vale_buy_price = last_valbz - 5
                id_vale_buy += 5



        elif message['type'] == "trade":
            
            if message["symbol"] == "VALBZ":

                last_valbz = message["price"]
                
                if not initalized_valbz:

                    initalized_valbz = True

                    sell_valbz(exchange, last_valbz + 2, id_valbz_sell)
                    buy_valbz(exchange, last_valbz - 2, id_valbz_buy)
                    
                    sell_vale(exchange, last_valbz + 5, id_vale_sell)
                    buy_vale(exchange, last_valbz + 5, id_vale_buy)

        elif message['type'] == 'book':

            #find ratio of spread thing if it's too big then cancel and reissue order
            if message['symbol'] == "VALBZ":
                
                if initalized_valbz:
                    #spread for buying
                    if len(message['buy']) > 0:
                        spread1 = message['buy'][0][0] - my_valbz_buy_price
                        if spread1 > 2:
                            #print("cancel")
                            write_to_exchange(exchange, {"type": "cancel", "order_id": id_valbz_buy})
                            id_valbz_buy += 5
                            #print("reissue")
                            buy_valbz(exchange, last_valbz - 1, id_valbz_buy)
                            my_valbz_buy_price = last_valbz - 1

                    #spread for selling
                    if len(message['sell']) > 0:
                        spread2 = my_valbz_sell_price - message['sell'][0][0]
                        if spread2 > 2:
                            print("cancel sell")
                            write_to_exchange(exchange, {"type": "cancel", "order_id": id_valbz_sell})
                            id_valbz_sell += 5
                            print("reorder sell")
                            sell_valbz(exchange, last_valbz + 1, id_valbz_sell)
                            my_valbz_sell_price = last_valbz + 1

            #elif message['symbol'] == "VALE":
        elif message['type'] == "close":
            raise Exception("CLOSE!!!")






if __name__ == "__main__":
    main()













