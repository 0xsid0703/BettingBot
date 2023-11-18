from mongoengine import *
from datetime import datetime, timedelta
from .colManager import ColManager

import sys
sys.path.append ("..")
from utils.logging import eventLogger
from utils import getTimeRangeOfCountry

class Event(ColManager):
    def __init__(self, database):
        super().__init__(database, "Event")
    
    def saveList(self, dList):
        for d in dList:
            eventCount = self.manager.count_documents ({"eventId": d["eventId"]})
            if (eventCount > 0):
                updateObj = {}
                if len(d['eventVenue']) > 0: updateObj['eventVenue'] = d['eventVenue']
                if len(d['timeZone']) > 0: updateObj['timeZone'] = d['timeZone']
                if d['openDate'] is not None: updateObj['openDate'] = d['openDate']
                if len(d['countryCode']) > 0: updateObj['countryCode'] = d['countryCode']
                
                eventDocument = self.manager.find_one ({"eventId": d["eventId"]})
                updateMarkets = d['markets']
                addMarkets = []
                for market in eventDocument['markets']:
                    flg = False
                    for marketDocument in d['markets']:
                        if marketDocument['marketId'] == market['marketId']:
                            flg = True
                            break
                    if flg == False: addMarkets.append (market)
                
                updateObj['markets'] = updateMarkets + addMarkets
                self.manager.update_one(
                    {"eventId": d['eventId']},
                    {"$set": updateObj}
                )
            else:
                self.manager.insert_one (d)
    
    def getDocumentsByDate(self, dateStr, eventTypeIds, countryCode, marketType):
        [minDate, maxDate] = getTimeRangeOfCountry(dateStr, countryCode.upper())
        events = self.manager.find ({
            "eventVenue": {"$ne": ""},
            "countryCode": countryCode.upper(),
            "markets.marketStartTime": {"$gt": minDate, "$lt": maxDate},
            "markets.marketCatalogueDescription.marketType": marketType,
            "markets.marketCatalogueDescription.raceType": {"$ne": "Harness"}
        })
        return list(events)

    def getDocumentsByFromDate(self, dateStr, eventTypeIds, countryCode):
        [minDate, maxDate] = getTimeRangeOfCountry(dateStr, countryCode.upper())
        events = self.manager.find ({
            "eventVenue": {"$ne": ""},
            "countryCode": countryCode.upper(),
            "markets.marketStartTime": {"$gt": minDate},
            "markets.marketCatalogueDescription.marketType": "WIN",
            "markets.marketCatalogueDescription.raceType": {"$ne": "Harness"}
        })

        return list(events)

    def getDocumentsByMarketId(self, market_id):
        events = self.manager.find({"markets.marketId": market_id})
        return list(events)
    
    def getTotalMatchedByNum(self, dateObj, trackName):
        event = self.manager.find_one ({"eventVenue": trackName, "markets.marketStartTime": dateObj }, {"markets.totalMatched": 1, "markets.marketStartTime": 1, "markets.marketCatalogueDescription.marketType": 1})
        event1 = self.manager.find_one ({"eventVenue": trackName, "markets.marketStartTime": dateObj + timedelta(hours = 1) }, {"markets.totalMatched": 1, "markets.marketStartTime": 1, "markets.marketCatalogueDescription.marketType": 1})

        if event is None and event1 is None: return 0
        if event is None and event1 is not None: 
            event  = event1
            dateObj += timedelta(hours = 1)
        totalMatched = 0
        for market in event['markets']:
            if dateObj.strftime("%Y-%m-%d %H:%M:%S") == market['marketStartTime'].strftime("%Y-%m-%d %H:%M:%S") and market['marketCatalogueDescription']['marketType'] == "WIN":
                totalMatched = market['totalMatched']
        return float(totalMatched)
    
    def getMarketByNum(self, dateObj, trackName):
        print (dateObj, "HHHHHHHHHHH")
        event = self.manager.find_one ({"eventVenue": trackName, "markets.marketStartTime": dateObj })
        event1 = self.manager.find_one ({"eventVenue": trackName, "markets.marketStartTime": dateObj + timedelta(hours = 1) })
        print (event is None, event1 is None, "PPPPPPPPPPP")
        if event is None and event1 is None: return None
        if event is None and event1 is not None: 
            event  = event1
            dateObj += timedelta(hours = 1)

        for market in event['markets']:
            if dateObj.strftime("%Y-%m-%d %H:%M:%S") == market['marketStartTime'].strftime("%Y-%m-%d %H:%M:%S") and market['marketCatalogueDescription']['marketType'] == "WIN":
                return market
        return None
    
    def getTotalMatchedByID(self, marketId):
        event = self.manager.find_one ({"markets.marketId": marketId }, {"markets.totalMatched": 1, "markets.marketId": 1, "markets.marketCatalogueDescription.marketType": 1})
        if event is None: return 0
        totalMatched = 0
        for market in event['markets']:
            if market['marketId'] == marketId and market['marketCatalogueDescription']['marketType'] == "WIN":
                totalMatched = market['totalMatched']
        return float(totalMatched)