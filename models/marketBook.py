from mongoengine import *
from datetime import timedelta
from .colManager import ColManager

import sys
sys.path.append ("..")
from utils.logging import marketBookLogger

class MarketBook(ColManager):
    def __init__(self, database):
        super().__init__(database, "MarketBook")
    
    def insert(self, mb):
        self.manager.insert_one (mb)
    
    def saveBook(self, mb):
        if mb['publishTime'] is None or mb['publishTime'] == '': return
        try:
            count = self.manager.count_documents ({'marketId': mb['marketId'], 'status': 'REMOVED'})
            if count > 1:
                return
            mbs = list(self.manager.find({'marketId': mb['marketId']}).sort("publishTime", -1))
            if len(mbs) == 0:
                self.manager.insert_one (mb)
                return
            sp = {}
            bsp = {}
            status = {}
            for runner in mb['runners']:
                sp[runner['selectionId']] = runner['sp']['nearPrice'] if 'nearPrice' in runner['sp'] else -1
                bsp[runner['selectionId']] = runner['sp']['actualSp'] if 'actualSp' in runner['sp'] else -1
                status[runner['selectionId']] = runner['status'] if 'status' in runner else ''
            for runner in mbs[0]['runners']:
                print (sp[runner['selectionId']] != runner['sp']['nearPrice'], runner['sp']['nearPrice'], sp[runner['selectionId']])
                if 'nearPrice' in runner['sp'] and sp[runner['selectionId']] != runner['sp']['nearPrice']:
                    self.manager.insert_one (mb)
                    return
                if 'actualSp' in runner['sp'] and bsp[runner['selectionId']] != runner['sp']['actualSp']:
                    self.manager.insert_one (mb)
                    return
                if 'status' in runner and status[runner['selectionId']] != runner['status']:
                    self.manager.insert_one (mb)
                    return
            # count = self.manager.count_documents ({'marketId': mb['marketId'], 'publishTime': mb['publishTime']})
            # if count > 0:
            #     return
            # else:
            #     self.manager.insert_one (mb)
        except Exception as e:
            print (e, "KKK")
            marketBookLogger.error ("saveBook() call failed", exc_info=True)
    
    def getDocumentsByID(self, market_id, match={}):
        match['marketId'] = market_id
        mbs = list(self.manager.find(match).sort("publishTime", -1))
        if len(mbs) == 0: return []
        tmp = []
        for mb in mbs:
            tmp_runners = []
            for runner in mb['runners']:
                if runner['status'] == 'ACTIVE':
                    tmp_runners.append (runner)
            mb['runners'] = tmp_runners
            tmp.append (mb)
        return tmp
    
    def getMarketBooksByIds(self, marketIds):
        mbs = self.manager.aggregate([
            {
                "$match": {
                    "marketId": { "$in": marketIds },
                    "status": "CLOSED",
                    "runners.status": "WINNER"
                }
            },
            {
                "$group": {
                    "_id": "$marketId",
                    "marketId": { "$first": "$marketId" },
                    "runners": {"$push": "$runners"}
                }
            }
        ])
        # mbs = self.manager.find({"marketId": {"$in": marketIds}, "runners.sp.actualSp": {"$ne": 0}})
        try:
            mbs = list(mbs)

            if len(mbs) == 0: return []
            tmp = []
            for mb in mbs:
                tmp_runners = []
                for runner in mb['runners'][0]:
                    if runner['status'] == 'ACTIVE' or runner['status'] == 'WINNER' or runner['status'] == 'LOSER':
                        runner['removalDate'] = runner['removalDate'].strftime("%Y-%m-%d %H:%M:%S") if 'removalDate' in runner and runner['removalDate'] is not None else ''
                        tmp_runners.append (runner)
                mb['runners'] = tmp_runners
                tmp.append (mb)
            return tmp
        except Exception as e:
            return []

    def getForRace (self, race_obj):
        mbs = list(self.manager.find({"marketDefinition.eventId": race_obj['event_id'], "runners.selectionId": race_obj['horse_id']}))
        if mbs is None: return None
        if len(mbs) == 0: return None
        return mbs[0]
    
    def getRecentMarketBookById(self, marketId):
        mbs = list(self.manager.find({"marketId": marketId}).sort("publishTime", -1).limit(1))
        if mbs is None: return None
        if len(mbs) == 0: return None
        return mbs[0]
    
    def getMarketBookByIdBefore(self, dateObj, marketId):
        mbsIn10 = list(self.manager.find({"marketId": marketId, "publishTime": {"$lte": dateObj - timedelta(minutes=10)}}).sort("publishTime", -1))
        mbsIn5 = list(self.manager.find({"marketId": marketId, "publishTime": {"$lte": dateObj - timedelta(minutes=5)}}).sort("publishTime", -1))
        if mbsIn10 is None: return None, None
        if len(mbsIn10) == 0: return None, None
        return mbsIn10[0], mbsIn5[0]