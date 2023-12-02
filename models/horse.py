from mongoengine import *
import datetime
from .colManager import ColManager

import math
import sys
sys.path.append ("..")
from utils.logging import horseLogger
from utils import getRegularClassStr, getClassPoint

class Horse(ColManager):
    def __init__(self, database):
        super().__init__(database, "Horse")
    
    def saveHorse(self, race_obj):
        try:
            horse_count = self.manager.count_documents ({"id": race_obj['horse_id']})
            if horse_count > 0:
                horses = self.manager.count_documents ({"id": race_obj['horse_id'], "races.track_id": race_obj['track_id']})

                if horses > 0:
                    return

                horses = list(self.manager.find ({"id": race_obj['horse_id']}))
                races = horses[0]['races']
                races.append (race_obj)
                self.manager.update_one(
                    {"id": race_obj['horse_id']},
                    {"$set": {"id": race_obj['horse_id'], "name": race_obj['horse_name'], "races": races}}
                )
            else:
                self.manager.insert_one ({
                    "id": race_obj['horse_id'],
                    "name": race_obj['horse_name'],
                    "races": [race_obj]
                })
        except:
            horseLogger.error ("saveHorse() failed.", exc_info=True)

    def getAllHorses(self, name):
        try:
            horses = self.manager.find ({"name": {"$regex" : name, "$options": "i"}})
            return horses
        except Exception as e:
            horseLogger.error ("getAllHorses() failed.", exc_info=True)

    def getHorseById(self, id):
        try:
            horse = self.manager.find_one ({"id": {"$in": [int(id), str(id)]}})
            return horse
        except:
            return None
    
    def getMaidenHorses(self, classValue, distance, condition, trackId):
            horses = self.manager.find ({"races": {"$size": 1}}).sort ("date", -1)
            horses = list(horses)
            horses = horses[:min(200, len(horses))]
            sumLastMgn = 0; sumLastFn = 0
            cntLastMgn = 0; cntLastFn = 0
            totalSpeed = 0; cntTotalSpeed = 0
            totalLast600 = 0; cntTotalLast600 = 0
            totalSettling = 0; cntTotalSettling = 0
            totalTrack = 0; cntTotalTrack = 0
            totalDistance = 0; cntTotalDistance = 0
            totalCondition = 0; cntTotalCondition = 0
            totalWin = 0; cntTotalWin = 0
            totalPlace = 0; cntTotalPlace = 0
            totalFinish = 0; cntTotalFinish = 0
            totalAvg = 0; cntTotalAvg = 0
            totalClass = 0; cntTotalClass = 0

            rlt = {}
            for horse in horses:
                r = horse['races'][0]
                r = dict (r)
                if "trial" in r['class'].lower(): continue
                cntTotalAvg += 1
                try:
                    totalFinish += float(r['finish_percentage']) if 'finish_percentage' in r else 0
                    cntTotalFinish += 1 if 'finish_percentage' in r and float(r['finish_percentage']) > 0 else 0
                except:
                    pass
                try:
                    totalAvg += int(r['horse_prizemoney'])
                except:
                    pass
                try:
                    if getRegularClassStr(classValue) == getRegularClassStr(r['class']):
                        totalClass += float(r['finish_percentage']) if 'finish_percentage' in r else 0
                        cntTotalClass += 1 if 'finish_percentage' in r and float(r['finish_percentage']) > 0 else 0
                except:
                    pass
                try:
                    if r['track_condition'].startswith(condition[0]):
                        totalCondition += float(r['finish_percentage'])
                        cntTotalCondition += 1 if 'finish_percentage' in r and float(r['finish_percentage']) > 0 else 0
                except:
                    pass
                try:
                    if math.ceil(int(r['distance'])/100) * 100 == math.ceil(int(distance)/100) * 100:
                        cntTotalDistance += 1 if 'finish_percentage' in r and float(r['finish_percentage']) > 0 else 0
                        totalDistance += float(r['finish_percentage']) if 'finish_percentage' in r else 0
                except:
                    pass
                try:
                    if int(r['track_id']) == int(trackId):
                        cntTotalTrack += 1 if 'finish_percentage' in r and float(r['finish_percentage']) > 0 else 0
                        totalTrack += float(r['finish_percentage']) if 'finish_percentage' in r else 0
                except:
                    pass
                try:
                    totalSettling += int(r['settling']) if 'settling' in r else 0
                    cntTotalSettling += 1 if int(r['settling']) > 0 else 0
                except:
                    pass
                try:
                    totalWin += int(r['win_percentage']) if 'win_percentage' in r else 0
                    cntTotalWin += 1 if 'win_percentage' in r and int(r['win_percentage']) > 0 else 0
                except:
                    pass
                try:
                    totalPlace += int(r['place_percentage']) if 'place_percentage' in r else 0
                    cntTotalPlace += 1 if 'place_percentage' in r and int(r['place_percentage']) > 0 else 0
                except:
                    pass
                try:
                    
                    totalLast600 += float(r['last_600'])
                    if 'last_600' in r and r['last_600'] > 0: cntLast600 += 1
                except:
                    pass
                try:
                    if isinstance(r['speed'], str):
                        continue
                    else:
                        totalSpeed += float(r['speed']) * 3.6
                        cntTotalSpeed += 1 if float(r['speed']) > 0 else 0
                except:
                    pass
            rlt['lastFn'] = float(horses[0]['races'][0]['finish_percentage'])
            rlt['lastMgn'] = float(horses[0]['races'][0]['margin'])
            rlt['speed'] =  "{:.2f}".format(totalSpeed/cntTotalSpeed) if cntTotalSpeed > 0 else "0"
            rlt['last_600'] = "{:.2f}".format(totalLast600/cntTotalLast600) if cntTotalLast600 > 0 else "0"
            rlt['settling'] = "{:.2f}".format(totalSettling/cntTotalSettling) if cntTotalSettling > 0 else "0"
            rlt['track'] = "{:.2f}".format(totalTrack/cntTotalTrack) if cntTotalTrack > 0 else "0"
            rlt['distance'] = "{:.2f}".format(totalDistance/cntTotalDistance) if cntTotalDistance > 0 else "0"
            rlt['condition'] = "{:.2f}".format(totalCondition/cntTotalCondition) if cntTotalCondition > 0 else "0"
            rlt['placePercent'] = "{:.2f}".format(totalPlace/cntTotalPlace) if cntTotalPlace > 0 else "0"
            rlt['winPercent'] = "{:.2f}".format(totalWin/cntTotalWin) if cntTotalWin > 0 else "0"
            rlt['finishPercent'] = "{:.2f}".format(totalFinish/cntTotalFinish) if cntTotalFinish > 0 else "0"
            rlt['average'] = "{:.2f}".format(totalAvg/cntTotalAvg) if cntTotalAvg > 0 else "0"
            rlt['class'] = "{:.2f}".format(totalClass/cntTotalClass) if cntTotalClass > 0 else "0"
            return rlt