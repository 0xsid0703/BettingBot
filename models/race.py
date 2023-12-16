from mongoengine import *
import datetime
from .colManager import ColManager
from .horse import Horse

import sys
sys.path.append ("..")
from utils.logging import raceLogger

class Race(ColManager):
    def __init__(self, database):
        super().__init__(database, "Race")
    
    def saveRace(self, race_obj, type = 0):
        try:
            if type == 0:
                cnt = self.manager.count_documents ({
                    "home_date":race_obj['home_date'],
                    "home_race_num":race_obj['home_race_num'],
                    "date": race_obj['date'],
                    "race_num": race_obj['race_num'],
                    "track_id": race_obj['track_id'],
                    "horse_id": race_obj['horse_id']
                })
                if cnt > 0:
                    self.manager.update_one(
                        {"home_date":race_obj['home_date'], "home_race_num":race_obj['home_race_num'], "date":race_obj['date'], "race_num": race_obj['race_num'], "track_id": race_obj['track_id'], "horse_id": race_obj['horse_id']},
                        {"$set": race_obj}
                    )
                else:
                    self.manager.insert_one (race_obj)
            elif type == 1:
                cnt = self.manager.count_documents ({"date":race_obj['date'], "main_race_num": race_obj['main_race_num'], "main_track_id": race_obj['main_track_id'], "horse_id": race_obj['horse_id']})
                if cnt > 0:
                    self.manager.update_many(
                        {"date":race_obj['date'], "main_race_num": race_obj['main_race_num'], "main_track_id": race_obj['main_track_id'], "horse_id": race_obj['horse_id']},
                        {"$set": race_obj}
                    )
                else:
                    self.manager.insert_one (race_obj)
        except:
            raceLogger.error ("saveRace() failed.", exc_info=True)
    
    def getRacesByHorse(self, horse_id):
        races = list(self.manager.find({"horse_id": {"$in": [int(horse_id), str(horse_id)]}, "settling": {"$gt": 0}}).sort("date", -1))
        return races

    def getRacesByTrainer(self, trainer_id):
        races = list(self.manager.find({"trainer_id": int(trainer_id), "settling": {"$gt": 0}}).sort("date", -1))
        return races
    
    def getRacesByJockey(self, jockey_id):
        races = list(self.manager.find({"jockey_id": int(jockey_id), "settling": {"$gt": 0}}).sort("date", -1))
        return races
    
    def getMainRaceByNum(self, date_obj, track_name, race_num):
        if date_obj == "undefined" or track_name == "undefined" or race_num == "undefined": return []
        races = self.manager.find({
            "main_track_name": {"$regex": track_name},
            "main_race_num": {"$in": [int(race_num), str(race_num)]},
            "date": date_obj
        })
        if races is None:
            races = self.manager.find({
                "main_race_name": {"$regex": track_name},
                "main_race_num": {"$in": [int(race_num), str(race_num)]},
                "date": date_obj
            })
            if races is None:
                return None
            return list(races)
        else:
            races = list(races)
            if len(races) > 0:
                return races
            else:
                races = self.manager.find({
                    "main_track_club": {"$regex": track_name},
                    "main_race_num": {"$in": [int(race_num), str(race_num)]},
                    "date": date_obj
                })
                if races is None:
                    return None
                else:
                    return list(races)
    
    def getRacesByHorseId(self, date_obj, track_name, race_num, horse_id):
        match = {}
        if date_obj is not None:
            match = {"home_date": date_obj}
        if track_name is not None:
            match['home_track_name'] = {"$regex": track_name}
        if race_num is not None:
            match['home_race_num'] = {"$in": [int(race_num), str(race_num)]}
        if horse_id is not None:
            match['horse_id'] = {"$in": [int(horse_id), str(horse_id)]}
        races = self.manager.find(match).sort("date", -1)
        return list(races)
    
    def getRacesByJockeyId(self, date_obj, track_name, race_num, jockey_id):
        match = {}
        if date_obj is not None:
            match = {"home_date": date_obj}
        if track_name is not None:
            match['home_track_name'] = {"$regex": track_name}
        if race_num is not None:
            match['home_race_num'] = race_num
        if jockey_id is not None:
            match['jockey_id'] = {"$in": [int(jockey_id), str(jockey_id)]}
        
        races = self.manager.find(match).sort("date", -1)
        return list(races)
    
    def getRacesByTrainerId(self, date_obj, track_name, race_num, trainer_id):
        match = {}
        if date_obj is not None:
            match = {"home_date": date_obj}
        if track_name is not None:
            match['home_track_name'] = {"$regex": track_name}
        if race_num is not None:
            match['home_race_num'] = race_num
        if trainer_id is not None:
            match['trainer_id'] = {"$in": [int(trainer_id), str(trainer_id)]}
        
        races = self.manager.find(match).sort("date", -1)
        return list(races)

    def removeRaceByDate(self, date_str):
        self.manager.delete_many ({'date': datetime.datetime.strptime(date_str, "%d/%m/%Y")})
        self.manager.delete_many ({'home_date': datetime.datetime.strptime(date_str, "%d/%m/%Y")})
    
    def getMainRacesByDate(self, dateStr):
        mainRaces = self.manager.find ({'date': datetime.datetime.strptime(dateStr, "%Y-%m-%d"), 'main_track_id': {'$ne': ''}, 'main_track_condition': {'$ne': ''}}).sort("main_race_num", 1)
        return mainRaces

    def setConditionOnMainRace(self, date_obj, track_name, race_num, condition):
        numRange = []
        for i in range(int(race_num), 20):
            numRange += [i, str(i)]
        races = self.manager.find({
            "main_track_name": {"$regex": track_name},
            "main_race_num": {"$in": numRange},
            "date": date_obj
        })
        if races is None:
            races = self.manager.find({
                "main_race_name": {"$regex": track_name},
                "main_race_num": {"$in": numRange},
                "date": date_obj
            })
            if races is None:
                return {"success": False}
            races = list(races)
            if len(races) > 0:
                races = self.manager.update_many({
                    "main_track_club": {"$regex": track_name},
                    "main_race_num": {"$in": numRange},
                    "date": date_obj
                },
                {
                    "$set": {"condition": condition}
                })
                return {"success": True}
            else:
                return {"success": False}
        else:
            races = list(races)
            if len(races) > 0:
                races = self.manager.update_many({
                    "main_track_name": {"$regex": track_name},
                    "main_race_num": {"$in": numRange},
                    "date": date_obj
                },
                {
                    "$set": {"condition": condition}
                })
                return {"success": True}
            else:
                races = self.manager.find({
                    "main_track_club": {"$regex": track_name},
                    "main_race_num": {"$in": numRange},
                    "date": date_obj
                })
                if races is None:
                    return {"success": False}
                else:
                    races = list(races)
                    if len(races) > 0:
                        races = self.manager.update_many({
                            "main_track_club": {"$regex": track_name},
                            "main_race_num": {"$in": numRange},
                            "date": date_obj
                        },
                        {
                            "$set": {"condition": condition}
                        })
                        return {"success": True}
                    else:
                        return {"success": False}