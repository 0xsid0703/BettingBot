from mongoengine import *
import datetime
from .colManager import ColManager

import sys
sys.path.append ("..")
from utils.logging import raceLogger
import json
from bson import ObjectId

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime.datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        return json.JSONEncoder.default(self, o)
    
class StatisticalWeights(ColManager):
    def __init__(self, database):
        super().__init__(database, "StatisticalWeights")
    
    def saveStatisticalWeights(self, StatisticalWeight_obj):
        try:
            cnt = self.manager.count_documents ({
                "home_date":StatisticalWeight_obj['home_date'],
                "race_num":StatisticalWeight_obj['race_num'],
                "home_track_name": StatisticalWeight_obj['home_track_name'],
            })
            if cnt > 0:
                self.manager.update_one(
                    {"home_date":StatisticalWeight_obj['home_date'], "race_num":StatisticalWeight_obj['race_num'], "home_track_name":StatisticalWeight_obj['home_track_name']},
                    {"$set": StatisticalWeight_obj}
                )
            else:
                self.manager.insert_one (StatisticalWeight_obj)
        except:
            raceLogger.error ("saveRace() failed.", exc_info=True)
    
    def getStatisticalWeightOne(self, date_obj, trackName, raceNum):
        statisticalWeights = self.manager.find_one({
            "home_date": date_obj,
            "home_track_name": trackName,
            "race_num": str(raceNum),
        })
        if statisticalWeights is None:
            return None
        else:
            return JSONEncoder().encode(statisticalWeights)