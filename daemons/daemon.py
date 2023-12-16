
import os
import time
import json
from datetime import datetime
import threading

import sys
curDir = os.path.dirname(os.path.realpath(__file__))
rootDir = os.path.abspath(os.path.join(curDir, os.pardir))
sys.path.append (rootDir)
from betfairs.trading import tradingObj
from utils.logging import daemonLogger
from feedFromXML.src.parse import buildRaceProfile

from models.dbManager import dbManager

fd = open("./1.txt", "w"); fd.write("running"); fd.close()

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
            daemonLogger.info("===   Database Connection successful.   ===")
        except Exception as e:
            daemonLogger.error("Database connection failed.", exc_info=True)
            return
    except Exception as e:
        daemonLogger.error("config/db.json file read failed.", exc_info=True)
        return

def daemonSaveEvent(interval, event):
    while True:
        if event.is_set(): break
        events = tradingObj.getEvents(['au', 'sg', 'nz'], [7])
        dbManager.eventCol.saveList (events)
        time.sleep(interval)

def daemonSaveMarketBook(interval):
    while True:
        events = dbManager.eventCol.getDocumentsByDate (datetime.utcnow().strftime("%Y-%m-%d"), [7], ["AU", 'NZ', 'SG'])
        for event in events:
            for market in event['markets']:
                marketBooks = tradingObj.getMarketBooks ([market['marketId']])
                if len(marketBooks) > 0:
                    marketBook = marketBooks [0]
                    if marketBook['status'] == 'OPEN':
                        dbManager.marketBookCol.saveBook (marketBook)
        time.sleep (interval)

def daemonSaveXMLData():
    races, tracks = buildRaceProfile ()
    for race in races:
        dbManager.raceCol.saveRace (race)
        dbManager.trainerCol.saveTrainer (race)
        dbManager.jockeyCol.saveJockey (race)
        dbManager.horseCol.saveHorse (race)
    
    for track in tracks:
        dbManager.raceCol.saveRace (track, 1)

def downloadMedialityFiles():
    import files_sdk
    import requests
    try:
        with open('./config/credentials.json') as f:
            credConfig = json.load(f)
            appKey = credConfig['mediality_app_key']
        files_sdk.set_api_key(appKey)
        files = list(files_sdk.folder.list_for ("/Centaur/production-s3/kagan@icloud.com/mr_form"))
        for fileObj in files:
            p = fileObj.download()
            downloadUri = p['download_uri']
            res = requests.get (downloadUri)
            if res.status_code == 200:
                fileName = p['download_uri'].split ("/")[-1]
                destinationPath = os.path.join("./feedFromXML/data/mr_form", fileName)

                with open(destinationPath, 'wb') as file:
                    file.write(res.content)
    except:
        pass

def main():
    connectDatabase()

    daemonSaveXMLData ()

    # while True:
    #     evt = threading.Event()
    #     saveEvent = threading.Thread(target=daemonSaveEvent, args=(15,evt))
    #     # saveMarketBook = threading.Thread(target=daemonSaveMarketBook, args=(15,))
    #     saveEvent.start ()
    #     time.sleep (3600)
    #     evt.set ()
    #     print (">>>>>>>")
        # # time.sleep (30)

if __name__ == "__main__":
    main()
