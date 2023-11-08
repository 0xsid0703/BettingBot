import betfairlightweight
from .controller import Controller
from datetime import datetime
import sys
sys.path.append('..')
from models.dbManager import dbManager
from utils.JSONEncoder import JSONEncoder
from utils.constants import *
from utils.logging import boardControllerLogger

KEY_NAME = {
  "jockey": "jockey_name",
  "trainer": "trainer_name",
  "horse": "horse_name",
  "condition": "track_condition",
  "track": "track_name",
  "distance": "distance",
}

SORT_FIELD = {
    "NAME": 'name',
    "WIN_PERCENT": 'winPercent',
    "AVG_BSPW": 'averageBspw',
    "WIN_ROI": 'winRoi',
    "PLACE_PERCENT": 'placePercent',
    "AVG_BSPP": 'averageBspp',
    "PLACE_ROI": 'placeRoi',
    "FINISH_PERCENT": 'finishPercent',
    "AVG": 'average',
    "TOTAL": 'total'
}

class BoardController(Controller):

    def __init__(self):
        super().__init__()

    def isFilter(self, record, filter):
        if filter is None: return True
        for key in list(filter.keys()):
            if key.startswith ("ALL "): continue
            if key == "jockey" or key == "trainer" or key == "horse" or key == "condition":
                if filter[key] == record[KEY_NAME[key]]: return True
                else: return False
            if key == "distance":
                if filter[key] == "1000 - 1200":
                    if record[KEY_NAME[key]] < 1000 or record[KEY_NAME[key]] > 1200:
                        return False
                if filter[key] == "1300 - 1600":
                    if record[KEY_NAME[key]] < 1300 or record[KEY_NAME[key]] > 1600:
                        return False
                if filter[key] == "1800 - 2200":
                    if record[KEY_NAME[key]] < 1800 or record[KEY_NAME[key]] > 2200:
                        return False
                if filter[key] == "2400+":
                    if record[KEY_NAME[key]] < 2400: return False
        return True
    
    def getLeaderBoards(self, filter, kind, page, sortedCol, sortDirection):
        records = []
        if kind == "trainer": records = list(dbManager.trainerCol.getRecordsByFilter(filter))
        elif kind == "horse": records = list(dbManager.horseCol.getRecordsByFilter(filter))
        elif kind == "jockey": records = list(dbManager.jockeyCol.getRecordsByFilter(filter))

        rlt = []
        for record in records:
            tmp = {}
            tmp['races'] = []
            tmp['id'] = record['id']
            tmp['name'] = record['name']
            sumWinPercent = 0
            sumPlacePercent = 0
            sumFinishPercent = 0
            sumPrize = 0
            for race in record['races']:
                if "_id" in race: race["_id"] = str(race["_id"])
                sumWinPercent += float(race['win_percentage'])
                sumPlacePercent += float(race['place_percentage'])
                sumFinishPercent += float(race['finish_percentage'])
                sumPrize += float(race['horse_prizemoney'])
                # race['horse_foaling_date'] = race['horse_foaling_date'].strftime("%d/%m/%y")
                # race['date'] = race['date'].strftime("%d/%m/%y")
                # tmp['races'].append (race)
            rlt.append ({
                "id": record['id'],
                "name": record['name'],
                "winPercent": round((sumWinPercent / len(record['races'])), 2) if len(record['races']) > 0 else 0,
                "placePercent": round((sumPlacePercent / len(record['races'])), 2) if len(record['races']) > 0 else 0,
                "finishPercent": round((sumFinishPercent / len(record['races'])), 2) if len(record['races']) > 0 else 0,
                "total": sumPrize,
                "average": round((sumPrize / len(record['races'])), 2) if len(record['races']) > 0 else 0,
            })
        
        def sortFunc(record):
            return record[sortedCol]
        
        rlt.sort (key = sortFunc, reverse=True if sortDirection == 1 else False)
        
        return rlt[20 * page : min(20 * (page + 1), len(rlt))]

    def getTrainernames(self, name):
        trainers = list(dbManager.trainerCol.getAllTrainers (name))
        rltTrainers = [trainer['name'] for trainer in trainers if len(trainer['name']) > 0]
        rltTrainers.sort ()
        return rltTrainers[0: min(20, len(rltTrainers))]
    
    def getHorsenames(self, name):
        horses = list(dbManager.horseCol.getAllHorses (name))
        rltHorses = [horse['name'] for horse in horses if len(horse['name']) > 0]
        rltHorses.sort ()
        return rltHorses[0: min(20, len(rltHorses))]
    
    def getJockeynames(self, name):
        jockeys = list(dbManager.jockeyCol.getAllJockeys (name))
        rltJockeys = [jockey['name'] for jockey in jockeys if len(jockey['name']) > 0]
        rltJockeys.sort ()
        return rltJockeys[0: min(20, len(rltJockeys))]