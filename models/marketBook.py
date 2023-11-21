from mongoengine import *
import datetime
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
        if mb['publishTime'] is None or mb['version'] == '': return
        try:
            count = self.manager.count_documents ({'marketId': mb['marketId'], 'status': 'REMOVED'})
            if count > 1:
                return
            count = self.manager.count_documents ({'marketId': mb['marketId'], 'version': mb['version']})
            if count > 0:
                return
            else:
                self.manager.insert_one (mb)
        except:
            marketBookLogger.error ("saveBook() call failed", exc_info=True)
    
    def getDocumentsByID(self, market_id, match={}):
        match['marketId'] = market_id
        mbs = list(self.manager.find(match).sort("version", -1))
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
        mbs = list(self.manager.find({"marketId": marketId}).sort("version", -1))
        if mbs is None: return None
        if len(mbs) == 0: return None
        return mbs[0]