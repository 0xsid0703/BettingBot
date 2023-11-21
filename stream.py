import multiprocessing
import threading
import json
from betfairs.trading import tradingObj
from betfairlightweight import StreamListener
from betfairlightweight.filters import (
    streaming_market_filter,
    streaming_market_data_filter,
)

from utils.logging import streamLogger

from models.dbManager import dbManager
import queue
import time
from datetime import datetime, timedelta
import os

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

def heartbeat(stream):
    """Send a heartbeat message to keep the connection alive."""
    while True:
        try:
            stream.heartbeat()
            print("Heartbeat sent to keep the stream alive.")
        except Exception as e:
            print("Heartbeat failed:", str(e))
            time.sleep(5)
        time.sleep(300)  # Send a heartbeat every 5 minutes

def start_stream(stream, listener):
    """Start the stream and handle reconnection if needed."""
    while True:
        try:
            stream.start()
        except Exception as e:
            print("Stream error:", str(e))
            print("Attempting to restart the stream.")
            time.sleep(10)  # Wait for 10 seconds before attempting to reconnect

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
            stream_thread = threading.Thread(target=start_stream, args=(stream, listener))
            stream_thread.start()
            heartbeat_thread = threading.Thread(target=heartbeat, args=(stream,))
            heartbeat_thread.start()
            print ("Start capture market thread...")
        except Exception as e:
            streamLogger.error("start failed.", exc_info=True)
        pass

        while True:
            print ("Capture queue data started...")
            marketBooks = output_queue.get()
            print (len(marketBooks), ">>> poped")
            
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
                        marketBook['version']
                    )
                except:
                    pass

def sortFunc (item):
    return item[1].timestamp()

def captureMarkets(processList):
    while True:
        events = tradingObj.getEvents(['au', 'nz', 'sg'], [7])
        winMarkets = []
        placeMarkets = []
        for event in events:
            for market in event['markets']:
                if market['marketCatalogueDescription']['marketType'] == "WIN":
                    if (datetime.utcnow() - timedelta(hours=1)) <  market['marketStartTime'] and datetime.utcnow().strftime("%Y-%m-%d") == (market['marketStartTime'] + timedelta(hours=10)).strftime("%Y-%m-%d"):
                        winMarkets.append ([market['marketId'], market['marketStartTime']])
                if market['marketCatalogueDescription']['marketType'] == "PLACE":
                    if (datetime.utcnow() - timedelta(hours=1)) <  market['marketStartTime'] and datetime.utcnow().strftime("%Y-%m-%d") == (market['marketStartTime'] + timedelta(hours=10)).strftime("%Y-%m-%d"):
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

            print ("capture markets started...")
            
            print (len(winMarkets))
            if len(winMarkets) == 0 and len(placeMarkets) == 0:
                time.sleep (3600)
            else:
                winMarkets.sort (key=sortFunc)
                placeMarkets.sort (key=sortFunc)
                
                if len(winMarkets) > 0:
                    wm = MarketBookCather([item[0] for item in winMarkets])
                    processList.append (wm.pid)
                if len(placeMarkets) > 0:
                    pm = MarketBookCather([item[0] for item in placeMarkets])
                    processList.append (pm.pid)
                try:
                    if (winMarkets[0][1] - datetime.now()).total_seconds() > 0:
                        if (winMarkets[0][1] - datetime.now()).total_seconds() > 3600:
                            time.sleep (3600)
                    else:
                        break
                    print (processList, "processList >>>>")
                except:
                    pass
            time.sleep (10)
            if (datetime.now() - startLoop).total_seconds() > 18000: break

def main():
    fd = open("./1.txt", "w");fd.write("Stream running");fd.close()
    connectDatabase()
    with multiprocessing.Manager() as manager:
        processList = manager.list()
        
        cm = multiprocessing.Process(target=captureMarkets, args=(processList, ))
        cm.start()
        
        cm.join()
    

main()