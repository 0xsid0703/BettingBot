import betfairlightweight
import pandas as pd
from .controller import Controller
from datetime import datetime
import sys
sys.path.append('..')
from models.dbManager import dbManager
from utils.JSONEncoder import JSONEncoder
from utils.constants import *
from utils.logging import basicControllerLogger

class BasicController(Controller):

    def __init__(self):
        super().__init__()

    def getEvents(self, betDate, eventTypeIds, countryCodeList, marketType):
        if eventTypeIds is None or len(eventTypeIds) == 0:
            return {
                "success": False,
                "msg": "Event type id array parameter should be not empty. Check this parameter again."
            }

        mainRaces = dbManager.raceCol.getMainRacesByDate (betDate)
        condition = {}
        for mainRace in mainRaces:
            if 'main_track_name' not in mainRace: continue
            if mainRace['main_track_name'] is None: continue
            if len(mainRace['main_track_name']) == 0: continue
            if mainRace['main_track_country'] == 'SGP':
                condition['Singapore'] = mainRace['main_track_condition']
            # if mainRace['main_track_club'] in condition:
            #     if mainRace['main_race_num'] in condition[mainRace['main_track_club']]:
            #         continue
            #     else:
            #         condition[mainRace['main_track_club']] = mainRace['main_track_condition']
            # else:
            condition[mainRace['main_track_club']] = mainRace['condition'] if 'condition' in mainRace else mainRace['main_track_condition']
            # if mainRace['main_track_name'] in condition:
            #     if mainRace['main_race_num'] in condition[mainRace['main_track_name']]:
            #         continue
            #     else:
            #         condition[mainRace['main_track_name']] = mainRace['main_track_condition']
            # else:
            condition[mainRace['main_track_name']] = mainRace['condition'] if 'condition' in mainRace else mainRace['main_track_condition']

        eList = dbManager.eventCol.getDocumentsByDate (betDate, eventTypeIds, countryCodeList, marketType)
        return self.getEventsFilterByType(eList, marketType, condition)

    def getUpcomingEvents(self, eventTypeIds, countryCodeList, marketType):
        if eventTypeIds is None or len(eventTypeIds) == 0:
            return {
                "success": False,
                "msg": "Event type id array parameter should be not empty. Check this parameter again."
            }
        
        eList = dbManager.eventCol.getUpcomingDocuments (eventTypeIds, countryCodeList, marketType)
        return self.getEventsFilterByType(eList, marketType)

    def getEventsFilterByType(self, eventList, marketType, condition={}):
        data = []
        marketIds = []
        trackNames = list(condition.keys())
        
        def sortFunc(market):
            return market['marketStartTime'].timestamp()

        mapWinToPlace = {}
        for e in eventList:
            markets = e['markets']
            markets.sort (key=sortFunc)
            marketIds += [market['marketId'] for market in markets if market["marketCatalogueDescription"]['marketType'] == "PLACE"]
            for winMarket in markets:
                if winMarket["marketCatalogueDescription"]['marketType'] == "WIN":
                    for placeMarket in markets:
                        if placeMarket["marketCatalogueDescription"]['marketType'] == "PLACE" and winMarket['marketStartTime'] == placeMarket['marketStartTime']:
                            mapWinToPlace[winMarket['marketId']] = placeMarket['marketId']
                            break

        marketBooks = dbManager.marketBookCol.getMarketBooksByIds(marketIds)
        marketBookWithRunners = {marketBook['marketId']: marketBook['runners'] for marketBook in marketBooks}

        for e in eventList:
            if e['eventId'] == 32707774: continue
            if e['eventVenue'] == 'Sapphire Coast': continue
            e['_id'] = str(e['_id'])
            markets = e['markets']
            markets.sort (key=sortFunc)
            lastMarket = markets[-1]
            if lastMarket['marketStartTime'] > datetime.now():
                if lastMarket['marketBook']['status'] == 'CLOSED': continue
            tName = ''
            for trackName in trackNames:
                if e['eventVenue'] in trackName:
                    tName = trackName
            
            tmp = {
                "venue": e['eventVenue'],
                "countryCode": e['countryCode'],
                'condition': CONDITION[condition[tName][0]] if tName in condition and len(condition[tName]) > 0 else CONDITION[condition['Singapore'][0]] if 'Singapore' in condition and e['countryCode'] == 'SG' else '',
                "markets": [{"startTime": market['marketStartTime'].strftime("%Y-%m-%dT%H:%M:%SZ"),
                             "marketId": market['marketId'],
                             "venue": e['eventVenue'],
                             "status":market['marketBook']['status'] if 'marketBook' in market and 'status' in market['marketBook'] else 'CLOSED',
                             "totalMatched": market['totalMatched'],
                             "runners": marketBookWithRunners[mapWinToPlace[market['marketId']]] if market['marketId'] in mapWinToPlace and mapWinToPlace[market['marketId']] in marketBookWithRunners else [],
                             "runnersId": {runner['selectionId']: runner['sortPriority'] for runner in market['runners']}
                            } 
                            for market in markets if market["marketCatalogueDescription"]["marketType"] == marketType]
            }
            
            data.append (tmp)
        
        return {
            "success": True,
            "data": data,
        }

    '''
    req = 0: rest api request
    req = 1: full market book data
    req = 2: custome find
    '''
    def getMarketBookById(self, market_id, req = 0, match={}):
        try:
            if len(market_id) == 0:
                return {
                    "success": False, 
                    "msg": "Market ID parameter is invalid."
                }
            if req == 0 or req == 1:
                marketBook = dbManager.marketBookCol.getDocumentsByID (market_id)
                totalMatched = dbManager.eventCol.getTotalMatchedByID(market_id)

                if len(marketBook)==0:
                    return {
                        "success": False, 
                        "msg": "No market book data with this market id: %s." % market_id
                    }
                
                marketPercent = 0
                for runner in marketBook[0]['runners']:
                    marketPercent += 1 / float(runner['ex']['availableToBack'][0]['price']) if len(runner['ex']['availableToBack']) > 0 else 0
                
                if req == 0:
                    return {
                        "success": True,
                        "data": {
                            "totalMatched": totalMatched,
                            "marketPercent": marketPercent * 100,
                            # "totalAvailable": marketBook[0]['totalAvailable'],
                            "runnerLen": len(list(marketBook[0]['runners']))
                        }
                    }
                elif req == 1:
                    try:
                        return marketBook[0]
                    except Exception as e:
                        return None
            elif req == 2:
                marketBook = dbManager.marketBookCol.getDocumentsByID (market_id, match)
                try:
                    return marketBook[0]
                except Exception as e:
                    return None

            
        except Exception as e:
            basicControllerLogger.error ("getMarketBookById() call failed.", exc_info=True)
            return {
                "success": False,
                "msg": "server failed with getMarketBookById()"
            }

    def getRunners(self, market_id):
        try:
            if len(market_id) == 0:
                return {
                    "success": False, 
                    "msg": "Market ID parameter is invalid."
                }
            eventObj = dbManager.eventCol.getDocumentsByMarketId (market_id)
            if len(eventObj)==0:
                return {
                    "success": False, 
                    "msg": "No event data with this market id: %s." % market_id
                }
            eventObj = eventObj[0]
            rlt_market = None
            for market in eventObj['markets']:
                if market['marketId'] == market_id:
                    rlt_market = market
                    break
            if rlt_market is None:
                return {
                    "success": False, 
                    "msg": "No market data in event object with this market id: %s." % market_id
                }
            rlt = []
            for runner in rlt_market['runners']:
                metadata = runner['metadata']
                market_book = self.getMarketBookById (market_id, 1)
                market_book_sp = self.getMarketBookById (market_id, 2, {"status": "CLOSED"})
                betfair_odds = 0
                status = ''
                if market_book is not None and market_book['inplay'] == False:
                    try:
                        for book_runner in market_book['runners']:
                            if runner['selectionId'] == book_runner['selectionId']:
                                # if book_runner['ex'] == {}: break
                                # if 'availableToBack' not in dict(book_runner['ex']): break
                                # if len(book_runner['ex']['availableToBack']) == 0: break
                                # betfair_odds = int(book_runner['ex']['availableToBack'][0]['price']
                                if book_runner['sp'] == {}: break
                                if 'nearPrice' not in dict(book_runner['sp']): break
                                betfair_odds = book_runner['sp']['nearPrice']
                                if book_runner['status'] is not None and book_runner['status'] != 0 and book_runner['status'] != '':
                                    status = book_runner['status']
                                break
                    except:
                        pass
                if market_book_sp is not None and market_book['inplay'] == True:
                    try:
                        for book_runner in market_book_sp['runners']:
                            if runner['selectionId'] == book_runner['selectionId']:
                                if book_runner['sp'] == {}: break
                                if 'actualSp' not in dict(book_runner['sp']): break
                                betfair_odds = book_runner['sp']['actualSp']
                                break
                    except:
                        pass
                if (status == 'ACTIVE'):
                    rlt.append ({
                        "file": metadata['COLOURS_FILENAME'],
                        "priority": runner['sortPriority'],
                        "selectionId": runner['selectionId'],
                        "name": runner['runnerName'],
                        "jockeyName": metadata['JOCKEY_NAME'],
                        "clothNum": metadata['CLOTH_NUMBER'],
                        "betfairOdds": betfair_odds
                    })
            return {
                "success": True,
                "data": rlt
            }

        except Exception as e:
            basicControllerLogger.error ("getRunners() call failed.", exc_info=True)
            return {
                "success": False,
                "msg": "server failed with getRunners()"
            }
        
    def getTurnoverInDay(self, date):
        events =  self.getEvents(date, [7], 'AU')
        bankRoll = 0
        for event in events:
            for market in event['markets']:
                bankRoll += market['totalMatched']
        return bankRoll
    
    def getMarketbooksWinners(self, date, type):
        pass