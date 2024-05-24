import multiprocessing
import os
import threading
import json
import queue
import time
import argparse
from datetime import datetime, timedelta
from betfairlightweight import StreamListener
from betfairlightweight.filters import (
    streaming_market_filter,
    streaming_market_data_filter,
)

import sys
curDir = os.path.dirname(os.path.realpath(__file__))
rootDir = os.path.abspath(os.path.join(curDir, os.pardir))
sys.path.append (rootDir)
from betfairs.trading import tradingObj
from utils.logging import streamLogger
from models.dbManager import dbManager

output_queue = queue.Queue()

def connectDatabase():
    from mongoengine import connect
    try:
        with open('./config/db.json') as f:
            dbConfig = json.load(f)
            dbname = dbConfig['dbname']
            host = dbConfig['host']
            port = dbConfig['port']
            username = dbConfig['username']
            password = dbConfig['password']
        try:
            connect (db=dbname, username=username, password=password, host="mongodb://%s:%d/%s" %(host, port, dbname))
            streamLogger.info("===   Database Connection successful.   ===")
        except Exception as e:
            streamLogger.error("Database connection failed.", exc_info=True)
            return
    except Exception as e:
        streamLogger.error("config/db.json file read failed.", exc_info=True)
        return
    
class MarketBookCather:
    def __init__(self, markets):
        self.ids = markets
        processStart = multiprocessing.Process(target=self.start)
        processStart.start()
        self.pid = processStart.pid
    
    def start(self):
        print ("Start a market:", self.ids)
        listener = StreamListener(output_queue=output_queue)
        stream = tradingObj.trading.streaming.create_stream(listener=listener)
        market_filter = streaming_market_filter(
            market_ids=self.ids
        )
        market_data_filter = streaming_market_data_filter(
            fields=["SP_PROJECTED", "SP_PROJECTED", "EX_MARKET_DEF", "EX_BEST_OFFERS_DISP", "EX_BEST_OFFERS", "EX_ALL_OFFERS", "EX_TRADED", "EX_TRADED_VOL"], ladder_levels=3
        )
        try:
            streaming_unique_id = stream.subscribe_to_markets(
                market_filter=market_filter,
                market_data_filter=market_data_filter,
                conflate_ms=2000,  # send update every 1000ms
            )
            t = threading.Thread(target=stream.start, daemon=True)
            t.start()
        except Exception as e:
            streamLogger.error("start failed.", exc_info=True)
        pass

        while True:
            marketBooks = output_queue.get()
            
            mbs = tradingObj.convertMarketBookToData (marketBooks)
            for marketBook in mbs:
                dbManager.marketBookCol.saveBook (marketBook)
                # for runner in marketBook['runners']:
                try:
                    print(
                        marketBook['runners'][0]['sp']['actualSp'],
                        marketBook['runners'][0]['sp']['nearPrice'],
                        marketBook['runners'][0]['sp']['farPrice'],
                        marketBook['marketId'],
                        marketBook['version'],
                        marketBook['publishTime']
                    )
                except:
                    pass

def myKillProcess(processList):

    while True:
        print (processList, "kill process started")
        while len(processList) > 0:
            try:
                p = processList.pop()
                os.kill (p, 15)
                print ("Finish process: %d" % p)
            except ProcessLookupError:
                print (f"Process with ID {p} not found.")
        time.sleep (600)

def sortFunc (item):
    return item[1].timestamp()

def captureMarkets(processList):
    while True:
        if datetime.now().hour in [22,23,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]:
            events = tradingObj.getEvents(['au', 'nz', 'sg'], [7])
            winMarkets = []
            placeMarkets = []
            for event in events:
                for market in event['markets']:
                    if market['marketCatalogueDescription']['marketType'] == "WIN":
                        if (datetime.utcnow() + timedelta(hours=10)).strftime("%Y-%m-%d") == (market['marketStartTime'] + timedelta(hours=10)).strftime("%Y-%m-%d"):
                            winMarkets.append ([market['marketId'], market['marketStartTime']])
                    if market['marketCatalogueDescription']['marketType'] == "PLACE":
                        if (datetime.utcnow() + timedelta(hours=10)).strftime("%Y-%m-%d") == (market['marketStartTime'] + timedelta(hours=10)).strftime("%Y-%m-%d"):
                            placeMarkets.append ([market['marketId'], market['marketStartTime']])
            startLoop = datetime.now()

            while True:
                
                while len(processList) > 0:
                    try:
                        p = processList.pop()
                        print ("Kill process in captureMarkets: %d" % p)
                        os.kill (p, 15)
                    except ProcessLookupError:
                        print (f"Process with ID {p} not found.")

                if len(winMarkets) == 0 and len(placeMarkets) == 0:
                    # time.sleep (3600)
                    time.sleep(60)
                    break
                else:
                    winMarkets.sort (key=sortFunc)
                    placeMarkets.sort (key=sortFunc)
                    
                    if len(winMarkets) > 0:
                        wm = MarketBookCather([item[0] for item in winMarkets])
                        processList.append (wm.pid)
                    if len(placeMarkets) > 0:
                        pm = MarketBookCather([item[0] for item in placeMarkets])
                        processList.append (pm.pid)
                time.sleep (15)
                if (datetime.now() - startLoop).total_seconds() > 18000: break
                # if datetime.now().hour not in [22,23,0,1,2,3,4,5,6,7,8,9,10,11]:
                while len(processList) > 0:
                    try:
                        p = processList.pop()
                        print ("Kill process in captureMarkets: %d" % p)
                        os.kill (p, 15)
                    except ProcessLookupError:
                        print (f"Process with ID {p} not found.")
                break
        else:
            print ("$$$$$$$")
            time.sleep(60)

def main():

    parser = argparse.ArgumentParser(description="Horse Racing Server")
    parser.add_argument ("--start", help="RESP API Daemon Start", action="store_true")
    parser.add_argument ("--stop", help="RESP API Daemon Stop", action="store_true")
    args = parser.parse_args()

    if args.start:
        # pid = os.fork()
        # if pid > 0:
        fd = open("./stream-pid", "w"); fd.write (str(os.getpid())); fd.close()
        connectDatabase()
        with multiprocessing.Manager() as manager:
            processList = manager.list()
            cm = multiprocessing.Process(target=captureMarkets, args=(processList, ))
            cm.start()
            cm.join()
    
    elif args.stop:
        os.chdir(os.getcwd())
        fd = open ("./stream-pid", "r"); pid = fd.read(); fd.close()
        fd = os.popen ("kill %s" % pid.strip(), "r"); fd.close()
    
if __name__ == "__main__":
    main()
