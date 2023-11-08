import multiprocessing
import os
import threading
import json
import queue
import time
from datetime import datetime
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
        # self.startTimes = [market['marketStartTime'].timestamp() for market in markets]
        # self.queue = output_queue
        processStart = multiprocessing.Process(target=self.start)
        processStart.start()
        self.pid = processStart.pid
        # processStart.join()
    
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
                conflate_ms=1000,  # send update every 1000ms
            )
            t = threading.Thread(target=stream.start, daemon=True)
            t.start()
            print ("Start capture market thread...")
        except Exception as e:
            streamLogger.error("start failed.", exc_info=True)
        pass

        while True:
            print ("Capture queue data started...")
            marketBooks = output_queue.get()
            print (marketBooks, ">>> poped")
            
            mbs = tradingObj.convertMarketBookToData (marketBooks)

            for marketBook in mbs:
                dbManager.marketBookCol.saveBook (marketBook)
                for runner in marketBook['runners']:
                    try:
                        print(
                            runner['sp']['actualSp'],
                            runner['sp']['nearPrice'],
                            runner['sp']['farPrice'],
                            marketBook['marketId']
                        )
                    except:
                        pass

def myKillProcess(processList):

    while True:
        print (processList, "kill process started")
        while len(processList) > 0:
        # for p in processList:
            try:
                p = processList.pop()
                os.kill (p, 15)
                print ("Finish process: %d" % p)
            except ProcessLookupError:
                print (f"Process with ID {p} not found.")
        time.sleep (600)

def getQueueData(output_queue): 
    while True:
        print ("Capture queue data started...")
        marketBooks = output_queue.get()
        print (marketBooks, ">>> poped")
        
        mbs = tradingObj.convertMarketBookToData (marketBooks)

        for marketBook in mbs:
            dbManager.marketBookCol.saveBook (marketBook)
            for runner in marketBook['runners']:
                try:
                    print(
                        runner['sp']['actualSp'],
                        runner['sp']['nearPrice'],
                        runner['sp']['farPrice'],
                        marketBook['marketId']
                    )
                except:
                    pass

def captureMarkets(processList):
    while True:
        
        while len(processList) > 0:
            try:
                p = processList.pop()
                print ("Kill process in captureMarkets: %d" % p)
                os.kill (p, 15)
            except ProcessLookupError:
                print (f"Process with ID {p} not found.")

        events = tradingObj.getEvents('au', [7])
        winMarkets = []
        placeMarkets = []
        print ("capture markets started...")
        for event in events:
            # tmp = [market['marketId'] if market['marketCatalogueDescription']['marketType'] == "WIN" for market in event['markets']]
            for market in event['markets']:
                if market['marketCatalogueDescription']['marketType'] == "WIN":
                    winMarkets.append (market['marketId'])
                if market['marketCatalogueDescription']['marketType'] == "PLACE":
                    placeMarkets.append (market['marketId'])
        wm = MarketBookCather(winMarkets)
        pm = MarketBookCather(placeMarkets)
        processList.append (wm.pid)
        processList.append (pm.pid)
        print (processList, "processList >>>>")
        time.sleep (600)

def main():
    connectDatabase()
    with multiprocessing.Manager() as manager:
        processList = manager.list()
        # shared_queue = manager.Queue()
        
        cm = multiprocessing.Process(target=captureMarkets, args=(processList, ))
        cm.start()
        
        # kp = multiprocessing.Process(target=myKillProcess, args=(processList,))
        # kp.start()
        
        # gq = multiprocessing.Process(target=getQueueData, args=(shared_queue,))
        # gq.start()
        # kp.join()
        cm.join()
        # gq.join()
    

main()