import betfairlightweight
from .controller import Controller
from datetime import datetime
import sys
import pytz
import math
import pandas as pd
sys.path.append('..')
from models.dbManager import dbManager
from utils.JSONEncoder import JSONEncoder
from utils.constants import *
from utils.logging import boardControllerLogger
from utils import getRegularClassStr, getClassPoint

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

RACECARD_SORT_FIELD = {
    'NO': 'tab_no',
    'HORSE': 'horse_name',
    'JOCKEY': 'jockey_name',
    'STARTS': 'starts',
    'BARRIER': 'horse_barrier',
    'WEIGHT': 'weight',
    'SCORE': 'score',
    'FRAMED': 'framed_odds',
    'BETFAIR': 'betfair',
    'DIFF': 'diff',
    'TEN_DIFF': '10m',
    'FIVE_DIFF': '5m'
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
    
    def getFramedOdds(self, horseScores, marketBook):
        totalScore = 0
        for key in list(horseScores.keys()):
            totalScore += horseScores[key]
        rawProb = {}
        for key in list(horseScores.keys()):
            rawProb[key] = horseScores[key] / totalScore
        
        totalProb = 0
        try:
            for runner in marketBook['runners']:
                if runner['status'] == 'REMOVED': continue
                if marketBook['status'] != "CLOSED":
                    totalProb += 1 / float(runner['ex']['availableToBack'][0]['price']) if len(runner['ex']['availableToBack']) > 0 else 0
                else:
                    totalProb += 1 / float(runner['sp']['actualSp'])
        except:
            pass

        adjt_factor = totalProb
        adjt_prob = {}
        framedOdds = {}
        for key in list(rawProb.keys()):
            adjt_prob[key] = rawProb[key] * adjt_factor
            framedOdds[key] = 1 / adjt_prob[key] if adjt_prob[key] > 0 else 0
        return framedOdds
    
    def getRaceByNum(self, dateStr, trackName, raceNum, condition, marketId=""):
        races = dbManager.raceCol.getMainRaceByNum(datetime.strptime(dateStr, "%Y-%m-%d"), trackName, raceNum)

        if races is None or (races is not None and len(list(races)) == 0):
            return None

        totalMatched = dbManager.eventCol.getTotalMatchedByNum(datetime.strptime(dateStr, "%Y-%m-%d"), races[0]['main_track_name'], int(raceNum))
        market = dbManager.eventCol.getMarketByNum(marketId)
        runners = []; statusRunners = {}
        framedOdds = None; horseScores = None; betfairs = {};betfairsIn10 = {}; betfairsIn5 = {}; bsp = {}
        if market is not None:
            marketBook = dbManager.marketBookCol.getRecentMarketBookById(market["marketId"])
            timePoint = (datetime.now() if datetime.now() < marketBook['marketDefinition']['marketTime'] else marketBook['marketDefinition']['marketTime']) if marketBook is not None else datetime.now()
            marketBook10, marketBook5 = dbManager.marketBookCol.getMarketBookByIdBefore(timePoint, market["marketId"])
            horseScores = self.getRaceHorseScores (dateStr, trackName, raceNum, condition, marketId)
            framedOdds = self.getFramedOdds (horseScores, marketBook)
            if marketBook is not None:
                tmpRunners = []
                marketStartTime = marketBook['marketDefinition']['marketTime']
                for runner in marketBook['runners']:
                    statusRunners[runner['selectionId']] = runner['status']
                    betfairs[runner['selectionId']] = float(runner['ex']['availableToBack'][0]['price']) if len(runner['ex']['availableToBack']) > 0 else 0
                    bsp[runner['selectionId']] = float(runner['sp']['nearPrice']) if marketStartTime > datetime.now() else float(runner['sp']['actualSp'])
                    if runner['status'].upper() != 'REMOVED': tmpRunners.append(runner['selectionId'])
                for runner in market['runners']:
                    if runner['selectionId'] in tmpRunners:
                        pams = runner['runnerName'].split(" ")
                        statusRunners[pams[0][:-1]] = statusRunners[runner['selectionId']]
                        betfairs[pams[0][:-1]] = betfairs[runner['selectionId']]
                        bsp[pams[0][:-1]] = bsp[runner['selectionId']]
                        runners.append (int(pams[0][:-1]))
            if marketBook10 is not None:
                for runner in marketBook10['runners']:
                    betfairsIn10[runner['selectionId']] = float(runner['ex']['availableToBack'][0]['price']) if len(runner['ex']['availableToBack']) > 0 else 0
                for runner in market['runners']:
                    if runner['selectionId'] in tmpRunners:
                        pams = runner['runnerName'].split(" ")
                        betfairsIn10[pams[0][:-1]] = betfairs[runner['selectionId']]
            if marketBook5 is not None:
                for runner in marketBook5['runners']:
                    betfairsIn5[runner['selectionId']] = float(runner['ex']['availableToBack'][0]['price']) if len(runner['ex']['availableToBack']) > 0 else 0
                for runner in market['runners']:
                    if runner['selectionId'] in tmpRunners:
                        pams = runner['runnerName'].split(" ")
                        betfairsIn5[pams[0][:-1]] = betfairs[runner['selectionId']]

        totalPrize = 0
        for item in races[0]['prizes']:
            if "total_value" in list(item.keys()):
                totalPrize = item['total_value']

        rlt = {
            "totalPrize": totalPrize,
            "totalMatched": totalMatched,
            "class": getClassPoint(getRegularClassStr(races[0]['class'])),
            "classStr": getRegularClassStr(races[0]['class']),
            "distance": races[0]['distance'],
            "startTime": races[0]['start_time'].strftime("%Y-%m-%d %H, %M:%S"),
        }
        horses = []
        for race in races:
            race = dict(race)
            if len(runners) > 0 and 'tab_no' in race and int(race['tab_no']) not in runners:
                continue
            tmpHorse = {}
            # horse = dbManager.horseCol.getHorseById (int(race['horse_id']))
            # horse = dict(horse)
            horseRaces = dbManager.raceCol.getRacesByHorseId(datetime.strptime(dateStr, "%Y-%m-%d"), trackName, int(raceNum), int(race['horse_id']))
            jockeyRaces = dbManager.raceCol.getRacesByJockeyId(None, None, None, int(race['main_jockey_id']))
            trainerRaces = dbManager.raceCol.getRacesByTrainerId(None, None, None, int(race['main_trainer_id']))

            sumFinishPercent = 0
            sumPrize = 0
            sumClass = 0
            sumFinish = 0
            sumCondition = 0
            sumDistance = 0;cntDistance = 0
            sumTrack = 0; cntTrack = 0
            sumTrainer = 0; cntTrainer = 0
            sumJockey = 0; cntJockey = 0
            sumSettling = 0; sumSpeed = 0
            sumLast600 = 0; cntLast600 = 0
            lastR = None; startDate = datetime.strptime("1970/01/01", "%Y/%m/%d")
            # if 'races' not in horse: horse['races'] = []
            cnt = 0
            for r in horseRaces:
                r = dict (r)
                if "trial" in r['class'].lower(): continue
                cnt += 1
                try:
                    sumFinishPercent += float(r['finish_percentage'])
                except:
                    pass
                try:
                    sumPrize += int(r['horse_prizemoney'])
                except:
                    pass
                try:
                    if getRegularClassStr(race['class']) == getRegularClassStr(r['class']): sumClass += float(r['finish_percentage'])
                except:
                    pass
                try:
                    sumFinish += float(r['finish_percentage'])
                except:
                    pass
                try:
                    if r['track_condition'].startswith(condition[0]): sumCondition += 1
                except:
                    pass
                try:
                    if math.ceil(int(r['distance'])/100) * 100 == math.ceil(int(race['distance'])/100) * 100:
                        cntDistance += 1
                        sumDistance += float(r['finish_percentage'])
                except:
                    pass
                try:
                    if int(r['track_id']) == int(race['main_track_id']):
                        cntTrack += 1
                        sumTrack += float(r['finish_percentage'])
                except:
                    pass
                
                try:
                    sumSettling += int(r['settling'])
                except:
                    pass
                try:
                    sumLast600 += float(r['last_600'])
                    if 'last_600' in r and r['last_600'] > 0: cntLast600 += 1
                except:
                    pass
                try:
                    sumSpeed += float(r['speed']) * 3.6
                except:
                    pass
                try:
                    if startDate < r['date']:
                        startDate = r['date']
                        lastR = r
                except:
                    pass
            
            
            for r in jockeyRaces:
                if cntJockey >= 200: break
                r = dict (r)
                if "trial" in r['class'].lower(): continue
                try:
                    sumJockey += float(r['finish_percentage'])
                except:
                    pass
                cntJockey += 1

            for r in trainerRaces:
                if cntTrainer >= 200: break
                r = dict (r)
                if "trial" in r['class'].lower(): continue
                try:
                    sumTrainer += float(r['finish_percentage'])
                except:
                    pass
                cntTrainer += 1
            
            tmpHorse['horse_name'] = race['horse_name'] if 'horse_name' in race else ''
            tmpHorse['jockey_name'] = race['main_jockey_name'] if 'main_jockey_name' in race else ''
            tmpHorse['jockey_id'] = race['main_jockey_id'] if 'main_jockey_id' in race else ''
            tmpHorse['horse_barrier'] = race['horse_barrier'] if 'horse_barrier' in race else 0
            tmpHorse['weight'] = race['weight_allocated'] if 'weight_allocated' in race else 0
            tmpHorse['class'] = "{:.2f}".format(sumClass/cnt) if cnt > 0 else 0
            tmpHorse['average'] = "{:.2f}".format(sumPrize/cnt) if cnt > 0 else 0
            tmpHorse['winPercent'] = race['win_percentage'] if 'win_percentage' in race else 0
            tmpHorse['placePercent'] = race['place_percentage'] if 'place_percentage' in race else 0
            tmpHorse['finishPercent'] = "{:.2f}".format(sumFinish/cnt) if cnt > 0 else 0
            tmpHorse['condition'] = "{:.2f}".format(sumCondition * 100/cnt) if cnt > 0 else 0
            tmpHorse['distance'] = "{:.2f}".format(sumDistance/cntDistance) if cntDistance > 0 else 0
            tmpHorse['track'] = "{:.2f}".format(sumTrack/cntTrack) if cntTrack > 0 else 0
            tmpHorse['trainer'] = "{:.2f}".format(sumTrainer/cntTrainer) if cntTrainer > 0 else 0
            tmpHorse['jockey'] = "{:.2f}".format(sumJockey/cntJockey) if cntJockey > 0 else 0
            tmpHorse['settling'] = "{:.2f}".format(sumSettling/cnt) if cnt > 0 else 0
            tmpHorse['last_600'] = "{:.2f}".format(sumLast600/cntLast600) if cntLast600 > 0 else 0
            tmpHorse['speed'] = "{:.2f}".format(sumSpeed/cnt) if cnt > 0 else 0
            tmpHorse['starts'] = cnt
            tmpHorse['tab_no'] = race['tab_no']
            tmpHorse['betfair'] = float(betfairs[str(race['tab_no'])]) if str(race['tab_no']) in betfairs else 0
            bspIn10 = float(betfairsIn10[str(race['tab_no'])]) if str(race['tab_no']) in betfairsIn10 else 0
            bspIn5 = float(betfairsIn5[str(race['tab_no'])]) if str(race['tab_no']) in betfairsIn5 else 0
            bspNow = float(bsp[str(race['tab_no'])]) if str(race['tab_no']) in bsp else 0
            tmpHorse['10m'] = (bspNow - bspIn10) * 100 / bspIn10 if bspIn10 > 0 else 100
            tmpHorse['5m'] = (bspNow - bspIn5) * 100 / bspIn5 if bspIn5 > 0 else 100
            tmpHorse['horse_silk'] = race['horse_silk'] if 'horse_silk' in race else ''
            tmpHorse['horse_id'] = race['horse_id']
            tmpHorse['status'] = statusRunners[str(race['tab_no'])] if 'tab_no' in race and str(race['tab_no']) in statusRunners else 'ACTIVE'
            hColor = COLOR_RESP[race['horse_colour']] if race['horse_colour'] in list(COLOR_RESP.keys()) else 'b'
            tmpHorse['gear'] = hColor
            if 'current_blinker_ind' in race and race['current_blinker_ind'] == 'Y':
                tmpHorse['gear'] = hColor + "-" + 'B'
            if len(race['gear_change']) > 0 and race['gear_change'][0]['option'] == 'first time' and 'blinkers' in race['gear_change'][0]['gear'].lower():
                tmpHorse['gear'] = hColor + "-" + 'BF'
            if len(race['gear_change']) > 0 and 'cross over nose' in race['gear_change'][0]['gear'].lower():
                tmpHorse['gear'] = hColor + "-" + 'CONB'
            if len(race['gear_change']) > 0 and 'ear muffs' in race['gear_change'][0]['gear'].lower():
                tmpHorse['gear'] = hColor + "-" + 'EM'
            if len(race['gear_change']) > 0 and 'nose roll' in race['gear_change'][0]['gear'].lower():
                tmpHorse['gear'] = hColor + "-" + 'NR'
            if len(race['gear_change']) > 0 and 'pacifier' in race['gear_change'][0]['gear'].lower():
                tmpHorse['gear'] = hColor + "-" + 'P'
            if len(race['gear_change']) > 0 and 'winker' in race['gear_change'][0]['gear'].lower():
                tmpHorse['gear'] = hColor + "-" + 'W'
            
            tmpHorse['framed_odds'] = framedOdds[tmpHorse['horse_name']] if framedOdds is not None and tmpHorse['horse_name'] in framedOdds else 0
            if lastR is not None:
                tmpHorse['lastFn'] = lastR['finish_percentage'] if 'finish_percentage' in lastR else 0
                tmpHorse['lastMgn'] = lastR['margin'] if 'margin' in lastR else 0
                if 'margin' in lastR:
                    try:
                        tmpHorse['lastMgn'] = 0 if int(lastR['finish_percentage']) == 100 else lastR['margin']
                    except:
                        tmpHorse['lastMgn'] = -1
                else:
                    tmpHorse['lastMgn'] = 0
            tmpHorse['score'] = horseScores[tmpHorse['horse_name']] if horseScores is not None and tmpHorse['horse_name'] in horseScores else 0
            tmpHorse['diff'] = (float(tmpHorse['betfair']) - float(tmpHorse['framed_odds'])) * 100 / float(tmpHorse['betfair']) if float(tmpHorse['betfair']) > 0 else 100
            horses.append (tmpHorse)
        rlt['horses'] =  horses
        return rlt
    
    def getFormScores(self, dateStr, trackName, raceNum, condition, marketId):
        races = dbManager.raceCol.getMainRaceByNum(datetime.strptime(dateStr, "%Y-%m-%d"), trackName, raceNum)
        if races is None or (races is not None and len(list(races)) == 0):
            return None

        curCondition = ''
        if 'condition' in races[0]:
            curCondition = CONDITION[races[0]['condition'][0]]
        else:
            curCondition = CONDITION[races[0]['main_track_condition'][0]] if 'main_track_condition' in races[0] else 'SOFT'
        data = self.getRankHorse(dateStr, trackName, raceNum, curCondition, marketId)
        return data

    def getRaceCardByNum(self, dateStr, trackName, raceNum, condition, marketId):
        jockeyNames = self.getJockeyNames (marketId)
        races = dbManager.raceCol.getMainRaceByNum(datetime.strptime(dateStr, "%Y-%m-%d"), trackName, raceNum)
        print (len(races), "RRRRRR")
        if races is None or (races is not None and len(list(races)) == 0):
            return None

        curCondition = ''
        if 'condition' in races[0]:
            curCondition = CONDITION[races[0]['condition'][0]]
        else:
            curCondition = CONDITION[races[0]['main_track_condition'][0]] if 'main_track_condition' in races[0] else 'SOFT'

        totalMatched = dbManager.eventCol.getTotalMatchedByNum(datetime.strptime(dateStr, "%Y-%m-%d"), races[0]['main_track_name'], int(raceNum))
        market = dbManager.eventCol.getMarketByNum(marketId)
        runners = []; statusRunners = {}
        framedOdds = None; horseScores = None; betfairs = {};betfairsIn10 = {}; betfairsIn5 = {}; bsp = {}
        winners = {}

        if market is not None:
            marketBook = dbManager.marketBookCol.getRecentMarketBookById(market["marketId"])
            timePoint = (datetime.now() if datetime.now() < marketBook['marketDefinition']['marketTime'] else marketBook['marketDefinition']['marketTime']) if marketBook is not None else datetime.now()
            marketBook10, marketBook5 = dbManager.marketBookCol.getMarketBookByIdBefore(timePoint, market["marketId"])
            horseScores = self.getRaceHorseScores (dateStr, trackName, raceNum, curCondition.capitalize(), marketId)
            framedOdds = self.getFramedOdds (horseScores, marketBook)
            if marketBook is not None:
                tmpRunners = []
                for runner in marketBook['runners']:
                    statusRunners[runner['selectionId']] = runner['status']
                    betfairs[runner['selectionId']] = float(runner['sp']['nearPrice']) if marketBook['status'] == "OPEN" else float(runner['sp']['actualSp'])
                    bsp[runner['selectionId']] = float(runner['ex']['availableToBack'][0]['price']) if len(runner['ex']['availableToBack']) > 0 and marketBook['status'] == "OPEN" else float(runner['sp']['actualSp'])
                    # bsp[runner['selectionId']] = float(runner['sp']['nearPrice']) if marketBook['status'] == "OPEN" else float(runner['sp']['actualSp'])
                    winners[runner['selectionId']] = runner['status'] if 'status' in runner else ''
                    if runner['status'].upper() != 'REMOVED': tmpRunners.append(runner['selectionId'])
                for runner in market['runners']:
                    if runner['selectionId'] in tmpRunners:
                        pams = runner['runnerName'].split(" ")
                        statusRunners[pams[0][:-1]] = statusRunners[runner['selectionId']]
                        betfairs[pams[0][:-1]] = betfairs[runner['selectionId']]
                        winners[pams[0][:-1]] = winners[runner['selectionId']]
                        bsp[pams[0][:-1]] = bsp[runner['selectionId']]
                        runners.append (int(pams[0][:-1]))
            if marketBook10 is not None:
                for runner in marketBook10['runners']:
                    betfairsIn10[runner['selectionId']] = float(runner['sp']['nearPrice']) if 'nearPrice' in runner['sp'] else 0
                    # betfairsIn10[runner['selectionId']] = float(runner['ex']['availableToBack'][0]['size']) if len(runner['ex']['availableToBack']) > 0 and marketBook['status'] == "OPEN" else float(runner['sp']['nearPrice'])
                for runner in market['runners']:
                    if runner['selectionId'] in tmpRunners:
                        pams = runner['runnerName'].split(" ")
                        betfairsIn10[pams[0][:-1]] = betfairsIn10[runner['selectionId']]
            if marketBook5 is not None:
                for runner in marketBook5['runners']:
                    betfairsIn5[runner['selectionId']] = float(runner['sp']['nearPrice']) if 'nearPrice' in runner['sp'] else 0
                    # betfairsIn5[runner['selectionId']] = float(runner['ex']['availableToBack'][0]['size']) if len(runner['ex']['availableToBack']) > 0 and marketBook['status'] == "OPEN" else float(runner['sp']['nearPrice'])
                for runner in market['runners']:
                    if runner['selectionId'] in tmpRunners:
                        pams = runner['runnerName'].split(" ")
                        betfairsIn5[pams[0][:-1]] = betfairsIn5[runner['selectionId']]

        totalPrize = 0
        for item in races[0]['prizes']:
            if "total_value" in list(item.keys()):
                totalPrize = item['total_value']
        
        rlt = {
            "totalPrize": totalPrize,
            "totalMatched": totalMatched,
            "class": getClassPoint(getRegularClassStr(races[0]['class'])),
            "classStr": getRegularClassStr(races[0]['class']),
            "distance": races[0]['distance'],
            "startTime": races[0]['start_time'].strftime("%Y-%m-%d %H, %M:%S"),
            "condition": curCondition
        }

        horses = []
        for race in races:
            race = dict(race)
            if len(runners) > 0 and 'tab_no' in race and int(race['tab_no']) not in runners:
                continue
            tmpHorse = {}
            horseRaces = dbManager.raceCol.getRacesByHorseId(datetime.strptime(dateStr, "%Y-%m-%d"), trackName, int(raceNum), int(race['horse_id']))

            startDate = datetime.strptime("1970/01/01", "%Y/%m/%d")
            # if 'races' not in horse: horse['races'] = []
            cnt = 0
            for r in horseRaces:
                r = dict (r)
                if "trial" in r['class'].lower(): continue
                cnt += 1
                try:
                    if startDate < r['date']:
                        startDate = r['date']
                except:
                    pass
            
            tmpHorse['horse_name'] = race['horse_name'] if 'horse_name' in race else ''
            if 'main_jockey_name' in race:
                if len(race['main_jockey_name']) > 0:
                    tmpHorse['jockey_name'] = race['main_jockey_name']
                else:
                    tmpHorse['jockey_name'] = jockeyNames[str(race['tab_no'])] if str(race['tab_no']) in jockeyNames else ''
            else:
                tmpHorse['jockey_name'] = jockeyNames[str(race['tab_no'])] if str(race['tab_no']) in jockeyNames else ''
            # tmpHorse['jockey_name'] = race['main_jockey_name'] if 'main_jockey_name' in race else ''
            tmpHorse['jockey_id'] = race['main_jockey_id'] if 'main_jockey_id' in race else ''
            tmpHorse['horse_barrier'] = race['horse_barrier'] if 'horse_barrier' in race else 0
            tmpHorse['weight'] = race['weight_allocated'] if 'weight_allocated' in race else 0
            tmpHorse['weight'] = float(tmpHorse['weight']) - float(race['main_jockey_allowance_weight']) if 'main_jockey_allowance_weight' in race else tmpHorse['weight']
            tmpHorse['starts'] = cnt
            tmpHorse['tab_no'] = race['tab_no']
            tmpHorse['status'] = winners[str(race['tab_no'])] if str(race['tab_no']) in winners else ''
            tmpHorse['betfair'] = float(betfairs[str(race['tab_no'])]) if str(race['tab_no']) in betfairs else 0
            tmpHorse['odds'] = float(bsp[str(race['tab_no'])]) if str(race['tab_no']) in bsp else 0
            bspIn10 = float(betfairsIn10[str(race['tab_no'])]) if str(race['tab_no']) in betfairsIn10 else 0
            bspIn5 = float(betfairsIn5[str(race['tab_no'])]) if str(race['tab_no']) in betfairsIn5 else 0
            bspNow = float(betfairs[str(race['tab_no'])]) if str(race['tab_no']) in betfairs else 0
            tmpHorse['10m'] = (bspNow - bspIn10) * 100 / bspIn10 if bspIn10 > 0 else 100
            tmpHorse['5m'] = (bspNow - bspIn5) * 100 / bspIn5 if bspIn5 > 0 else 100
            tmpHorse['horse_silk'] = race['horse_silk'] if 'horse_silk' in race else ''
            tmpHorse['horse_id'] = race['horse_id']
            tmpHorse['status'] = statusRunners[str(race['tab_no'])] if 'tab_no' in race and str(race['tab_no']) in statusRunners else 'ACTIVE'
            hColor = COLOR_RESP[race['horse_colour']] if race['horse_colour'] in list(COLOR_RESP.keys()) else 'b'
            tmpHorse['gear'] = hColor
            if 'current_blinker_ind' in race and race['current_blinker_ind'] == 'Y':
                tmpHorse['gear'] = hColor + "-" + 'B'
            if len(race['gear_change']) > 0 and race['gear_change'][0]['option'] == 'first time' and 'blinkers' in race['gear_change'][0]['gear'].lower():
                tmpHorse['gear'] = hColor + "-" + 'BF'
            if len(race['gear_change']) > 0 and 'cross over nose' in race['gear_change'][0]['gear'].lower():
                tmpHorse['gear'] = hColor + "-" + 'CONB'
            if len(race['gear_change']) > 0 and 'ear muffs' in race['gear_change'][0]['gear'].lower():
                tmpHorse['gear'] = hColor + "-" + 'EM'
            if len(race['gear_change']) > 0 and 'nose roll' in race['gear_change'][0]['gear'].lower():
                tmpHorse['gear'] = hColor + "-" + 'NR'
            if len(race['gear_change']) > 0 and 'pacifier' in race['gear_change'][0]['gear'].lower():
                tmpHorse['gear'] = hColor + "-" + 'P'
            if len(race['gear_change']) > 0 and 'winker' in race['gear_change'][0]['gear'].lower():
                tmpHorse['gear'] = hColor + "-" + 'W'
            
            tmpHorse['framed_odds'] = framedOdds[tmpHorse['horse_name']] if framedOdds is not None and tmpHorse['horse_name'] in framedOdds else 0
            
            tmpHorse['score'] = horseScores[tmpHorse['horse_name']] if horseScores is not None and tmpHorse['horse_name'] in horseScores else 0
            tmpHorse['diff'] = (float(tmpHorse['betfair']) - float(tmpHorse['framed_odds'])) * 100 / float(tmpHorse['framed_odds']) if float(tmpHorse['framed_odds']) > 0 else 100
            horses.append (tmpHorse)
        
        rlt['horses'] =  horses
        return rlt

    def getRaceFormByNum(self, dateStr, trackName, raceNum, condition, marketId):
        jockeyNames = self.getJockeyNames (marketId)
        races = dbManager.raceCol.getMainRaceByNum(datetime.strptime(dateStr, "%Y-%m-%d"), trackName, raceNum)

        if races is None or (races is not None and len(list(races)) == 0):
            return None

        curCondition = ''
        if 'condition' in races[0]:
            curCondition = CONDITION[races[0]['condition'][0]]
        else:
            curCondition = CONDITION[races[0]['main_track_condition'][0]] if 'main_track_condition' in races[0] else 'SOFT'

        totalMatched = dbManager.eventCol.getTotalMatchedByNum(datetime.strptime(dateStr, "%Y-%m-%d"), races[0]['main_track_name'], int(raceNum))
        market = dbManager.eventCol.getMarketByNum(marketId)
        runners = []; statusRunners = {}
        if market is not None:
            marketBook = dbManager.marketBookCol.getRecentMarketBookById(market["marketId"])
            if marketBook is not None:
                tmpRunners = []
                for runner in marketBook['runners']:
                    statusRunners[runner['selectionId']] = runner['status']
                    if runner['status'].upper() != 'REMOVED': tmpRunners.append(runner['selectionId'])
                for runner in market['runners']:
                    if runner['selectionId'] in tmpRunners:
                        pams = runner['runnerName'].split(" ")
                        statusRunners[pams[0][:-1]] = statusRunners[runner['selectionId']]
                        runners.append (int(pams[0][:-1]))

        totalPrize = 0
        for item in races[0]['prizes']:
            if "total_value" in list(item.keys()):
                totalPrize = item['total_value']
        
        rlt = {
            "totalPrize": totalPrize,
            "totalMatched": totalMatched,
            "class": getClassPoint(getRegularClassStr(races[0]['class'])),
            "classStr": getRegularClassStr(races[0]['class']),
            "distance": races[0]['distance'],
            "startTime": races[0]['start_time'].strftime("%Y-%m-%d %H, %M:%S"),
            'condition': curCondition
        }
        horses = []
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

        horseIds = []
        raceClass = races[0]['class']; raceDistance = races[0]['distance']; raceTrackId = races[0]['main_track_id']
        for race in races:
            race = dict(race)
            if len(runners) > 0 and 'tab_no' in race and int(race['tab_no']) not in runners:
                continue
            # maidenHorse = dbManager.horseCol.getMaidenHorses (race['class'], race['distance'], condition, race['main_track_id'])
            tmpHorse = {}
            # horse = dbManager.horseCol.getHorseById (int(race['horse_id']))
            # horse = dict(horse)
            horseRaces = dbManager.raceCol.getRacesByHorseId(datetime.strptime(dateStr, "%Y-%m-%d"), trackName, int(raceNum), int(race['horse_id']))
            # jockeyRaces = dbManager.raceCol.getRacesByJockeyId(None, None, None, int(race['main_jockey_id']))
            # trainerRaces = dbManager.raceCol.getRacesByTrainerId(None, None, None, int(race['main_trainer_id']))
            jockeyObj = dbManager.jockeyCol.getJockeyById(int(race['main_jockey_id']))
            trainerObj = dbManager.trainerCol.getTrainerById(int(race['main_trainer_id']))
            jockeyRaces = jockeyObj['races'] if 'races' in jockeyObj else []
            trainerRaces = trainerObj['races'] if 'races' in trainerObj else []

            sumFinishPercent = 0
            sumPrize = 0
            sumClass = 0
            sumFinish = 0
            sumCondition = 0
            sumDistance = 0;cntDistance = 0
            sumTrack = 0; cntTrack = 0
            sumTrainer = 0; cntTrainer = 0
            sumJockey = 0; cntJockey = 0
            sumSettling = 0; sumSpeed = 0
            sumLast600 = 0; cntLast600 = 0; cntSpeed = 0
            lastR = None; startDate = datetime.strptime("1970/01/01", "%Y/%m/%d")

            cnt = 0
            for r in horseRaces:
                r = dict (r)
                if "trial" in r['class'].lower(): continue
                cnt += 1
                try:
                    sumFinishPercent += float(r['finish_percentage'])
                except:
                    pass
                try:
                    sumPrize += int(r['horse_prizemoney'])
                except:
                    pass
                try:
                    if getRegularClassStr(race['class']) == getRegularClassStr(r['class']): sumClass += float(r['finish_percentage'])
                except:
                    pass
                try:
                    sumFinish += float(r['finish_percentage'])
                except:
                    pass
                try:
                    if 'condition' in r:
                        if r['condition'].startswith(curCondition[0]): sumCondition += 1
                    else:
                        if r['track_condition'].startswith(curCondition[0]): sumCondition += 1
                except:
                    pass
                try:
                    if math.ceil(int(r['distance'])/100) * 100 == math.ceil(int(race['distance'])/100) * 100:
                        cntDistance += 1
                        sumDistance += float(r['finish_percentage'])
                except:
                    pass
                try:
                    if int(r['track_id']) == int(race['main_track_id']):
                        cntTrack += 1
                        sumTrack += float(r['finish_percentage'])
                except:
                    pass
                
                try:
                    sumSettling += int(r['settling'])
                except:
                    pass
                try:
                    sumLast600 += float(r['last_600'])
                    if 'last_600' in r and r['last_600'] > 0: cntLast600 += 1
                except:
                    pass
                try:
                    if isinstance(r['speed'], str):
                        continue
                    else:
                        sumSpeed += float(r['speed']) * 3.6
                        cntSpeed += 1
                except:
                    pass
                try:
                    if startDate < r['date']:
                        startDate = r['date']
                        lastR = r
                except:
                    pass
            
            
            for r in jockeyRaces:
                if cntJockey >= 200: break
                r = dict (r)
                if "trial" in r['class'].lower(): continue
                try:
                    sumJockey += float(r['finish_percentage'])
                except:
                    pass
                cntJockey += 1

            for r in trainerRaces:
                if cntTrainer >= 200: break
                r = dict (r)
                if "trial" in r['class'].lower(): continue
                try:
                    sumTrainer += float(r['finish_percentage'])
                except:
                    pass
                cntTrainer += 1
            
            tmpHorse['horse_name'] = race['horse_name'] if 'horse_name' in race else ''
            if 'main_jockey_name' in race:
                if len(race['main_jockey_name']) > 0:
                    tmpHorse['jockey_name'] = race['main_jockey_name']
                else:
                    tmpHorse['jockey_name'] = jockeyNames[str(race['tab_no'])] if str(race['tab_no']) in jockeyNames else ''
            else:
                tmpHorse['jockey_name'] = jockeyNames[str(race['tab_no'])] if str(race['tab_no']) in jockeyNames else ''
            tmpHorse['jockey_id'] = race['main_jockey_id'] if 'main_jockey_id' in race else ''
            
            tmpHorse['class'] = "{:.2f}".format(sumClass/cnt) if cnt > 0 else 0
            cntTotalClass += 1 if cnt > 0 else 0
            totalClass += float(tmpHorse['class'])
            
            tmpHorse['average'] = "{:.2f}".format(sumPrize/cnt) if cnt > 0 else 0
            cntTotalAvg += 1 if cnt > 0 else 0
            totalAvg += float(tmpHorse['average'])
            
            tmpHorse['winPercent'] = race['win_percentage'] if 'win_percentage' in race else 0
            cntTotalWin += 1 if cnt > 0  else 0
            totalWin += float(tmpHorse['winPercent'])
            
            tmpHorse['placePercent'] = race['place_percentage'] if 'place_percentage' in race else 0
            cntTotalPlace += 1 if cnt > 0 else 0
            totalPlace += float(tmpHorse['placePercent'])
            
            tmpHorse['finishPercent'] = "{:.2f}".format(sumFinish/cnt) if cnt > 0 else 0
            cntTotalFinish += 1 if cnt > 0 else 0
            totalFinish += float(tmpHorse['finishPercent'])
            
            tmpHorse['condition'] = "{:.2f}".format(sumCondition * 100/cnt) if cnt > 0 else 0
            cntTotalCondition += 1 if cnt > 0 else 0
            totalCondition += float(tmpHorse['condition'])
            
            tmpHorse['distance'] = "{:.2f}".format(sumDistance/cntDistance) if cntDistance > 0 else 0
            cntTotalDistance += 1 if cntDistance > 0 else 0
            totalDistance += float(tmpHorse['distance'])
            
            tmpHorse['track'] = "{:.2f}".format(sumTrack/cntTrack) if cntTrack > 0 else 0
            cntTotalTrack += 1 if cnt > 0 else 0
            totalTrack += float(tmpHorse['track'])
            
            tmpHorse['trainer'] = "{:.2f}".format(sumTrainer/cntTrainer) if cntTrainer > 0 else 0
            tmpHorse['jockey'] = "{:.2f}".format(sumJockey/cntJockey) if cntJockey > 0 else 0
            
            tmpHorse['settling'] = "{:.2f}".format(sumSettling/cnt) if cnt > 0 else 0
            cntTotalSettling += 1 if cnt > 0 else 0
            totalSettling += float(tmpHorse['settling'])
            
            tmpHorse['last_600'] = "{:.2f}".format(sumLast600/cntLast600) if cntLast600 > 0 else 0
            cntTotalLast600 += 1 if cnt > 0 else 0
            totalLast600 += float(tmpHorse['last_600'])
            
            tmpHorse['speed'] = "{:.2f}".format(sumSpeed/cntSpeed) if cntSpeed > 0 else 0
            cntTotalSpeed += 1 if cnt > 0 else 0
            totalSpeed += float(tmpHorse['speed'])
            
            tmpHorse['starts'] = cnt
            tmpHorse['tab_no'] = race['tab_no']
            tmpHorse['horse_silk'] = race['horse_silk'] if 'horse_silk' in race else ''
            tmpHorse['horse_id'] = race['horse_id']; horseIds.append (race['horse_id'])
            tmpHorse['status'] = statusRunners[str(race['tab_no'])] if 'tab_no' in race and str(race['tab_no']) in statusRunners else 'ACTIVE'
            hColor = COLOR_RESP[race['horse_colour']] if race['horse_colour'] in list(COLOR_RESP.keys()) else 'b'
            tmpHorse['gear'] = hColor
            if 'current_blinker_ind' in race and race['current_blinker_ind'] == 'Y':
                tmpHorse['gear'] = hColor + "-" + 'B'
            if len(race['gear_change']) > 0 and race['gear_change'][0]['option'] == 'first time' and 'blinkers' in race['gear_change'][0]['gear'].lower():
                tmpHorse['gear'] = hColor + "-" + 'BF'
            if len(race['gear_change']) > 0 and 'cross over nose' in race['gear_change'][0]['gear'].lower():
                tmpHorse['gear'] = hColor + "-" + 'CONB'
            if len(race['gear_change']) > 0 and 'ear muffs' in race['gear_change'][0]['gear'].lower():
                tmpHorse['gear'] = hColor + "-" + 'EM'
            if len(race['gear_change']) > 0 and 'nose roll' in race['gear_change'][0]['gear'].lower():
                tmpHorse['gear'] = hColor + "-" + 'NR'
            if len(race['gear_change']) > 0 and 'pacifier' in race['gear_change'][0]['gear'].lower():
                tmpHorse['gear'] = hColor + "-" + 'P'
            if len(race['gear_change']) > 0 and 'winker' in race['gear_change'][0]['gear'].lower():
                tmpHorse['gear'] = hColor + "-" + 'W'
            
            tmpHorse['lastFn'] = -1
            tmpHorse['lastMgn'] = -1
            if lastR is not None:
                tmpHorse['lastFn'] = lastR['finish_percentage'] if 'finish_percentage' in lastR else -1
                tmpHorse['lastMgn'] = lastR['margin'] if 'margin' in lastR else -1
                tmpHorse['lastMgn'] = 0 if tmpHorse['lastFn'] == 100 else -1
                if 'margin' in lastR:
                    try:
                        tmpHorse['lastMgn'] = 0 if int(lastR['finish_percentage']) == 100 else lastR['margin']
                    except:
                        tmpHorse['lastMgn'] = -1
                else:
                    tmpHorse['lastMgn'] = -1
                if tmpHorse['lastMgn'] > -1:
                    sumLastMgn += tmpHorse['lastMgn']
                    cntLastMgn += 1
                if tmpHorse['lastFn'] > -1:
                    sumLastFn += tmpHorse['lastFn']
                    cntLastFn += 1
            horses.append (tmpHorse)
        avgFn = sumLastFn / cntLastFn if cntLastFn > 0 else 0
        avgMgn = sumLastMgn / cntLastMgn if cntLastMgn > 0 else 0

        firstRaces = dbManager.horseCol.getFirstRacesByIds (horseIds)
        cntNotMaiden = 0
        totalMaidenClass = 0; totalMaidenAvg = 0; totalMaidenFinish = 0; totalMaidenWin = 0; totalMaidenPlace = 0; totalMaidenCondition = 0; totalMaidenDistance = 0
        totalMaidenTrack = 0; totalMaidenLast600 = 0; totalMaidenSettling = 0; totalMaidenSpeed = 0
        for horse in horses:
            if str(horse['horse_id']) not in firstRaces: continue
            r = firstRaces[str(horse['horse_id'])] 
            if horse['starts'] > 0:
                # cntNotMaiden += 1
                # try:
                #     if getRegularClassStr(raceClass) == getRegularClassStr(r['class']): totalMaidenClass += float(r['finish_percentage'])
                # except:
                #     pass
                # try:
                #     totalMaidenAvg += int(r['horse_prizemoney'])
                # except:
                #     pass
                # try:
                #     totalMaidenFinish += int(r['finish_percentage'])
                # except:
                #     pass
                # try:
                #     totalMaidenWin += 100 if r['finish_number'] == 1 else 0
                # except:
                #     pass
                # try:
                #     totalMaidenPlace += int(r['finish_percentage']) if r['finish_number'] < 4 else 0
                # except:
                #     pass
                # try:
                #     if r['track_condition'].startswith(condition[0]): totalMaidenCondition += 1
                # except:
                #     pass
                # try:
                #     if math.ceil(int(r['distance'])/100) * 100 == math.ceil(int(raceDistance)/100) * 100:
                #         totalMaidenDistance += float(r['finish_percentage'])
                # except:
                #     pass
                # try:
                #     if int(r['track_id']) == int(raceTrackId):
                #         totalMaidenTrack += float(r['finish_percentage'])
                # except:
                #     pass
                # try:
                #     totalMaidenSettling += float(r['settling'])
                # except:
                #     pass
                try:
                    totalMaidenLast600 += float(r['last_600'])
                    cntNotMaiden += 1 if 'last_600' in r else 0
                except:
                    pass
                try:
                    totalMaidenSpeed += float(r['speed']) * 3.6 if float(r['speed']) < 25 else 75
                except:
                    pass

        tmpHorses = []
        for horse in horses:
            if horse['lastFn'] == -1: horse['lastFn'] = avgFn
            if horse['lastMgn'] == -1: horse['lastMgn'] = avgMgn
            if horse['starts'] > 0:
                # horse['speed'] = "{:.2f}".format(totalMaidenSpeed / cntNotMaiden) if cntNotMaiden > 0 and horse['speed'] == 0 else 0
                if float(horse['last_600']) == 0:
                    horse['last_600'] = "{:.2f}".format(totalMaidenLast600 / cntNotMaiden) if cntNotMaiden > 0 and float(horse['last_600']) == 0 else 0
                # horse['settling'] = "{:.2f}".format(totalMaidenSettling/ cntNotMaiden) if cntNotMaiden > 0 else 0
                # horse['distance'] = "{:.2f}".format(totalMaidenDistance/ cntNotMaiden) if cntNotMaiden > 0 else 0
                # horse['condition'] = "{:.2f}".format(totalMaidenCondition * 100/ cntNotMaiden) if cntNotMaiden > 0 else 0
                # horse['placePercent'] = "{:.2f}".format(totalMaidenPlace/ cntNotMaiden) if cntNotMaiden > 0 else 0
                # horse['winPercent'] = "{:.2f}".format(totalMaidenWin/ cntNotMaiden) if cntNotMaiden > 0 else 0
                # horse['finishPercent'] = "{:.2f}".format(totalMaidenFinish/ cntNotMaiden) if cntNotMaiden > 0 else 0
                # horse['track'] = "{:.2f}".format(totalMaidenTrack/ cntNotMaiden) if cntNotMaiden > 0 else 0
                # horse['average'] = "{:.2f}".format(totalMaidenAvg/ cntNotMaiden) if cntNotMaiden > 0 else 0
            else:
                if float(horse['speed']) == 0:
                    horse['speed'] =  "{:.2f}".format(totalSpeed/cntTotalSpeed) if cntTotalSpeed > 0 else "0"
                if float(horse['last_600']) == 0:
                    horse['last_600'] = "{:.2f}".format(totalLast600/cntTotalLast600) if cntTotalLast600 > 0 else "0"
                if float(horse['settling']) == 0:
                    horse['settling'] = "{:.2f}".format(totalSettling/cntTotalSettling) if cntTotalSettling > 0 else "0"
                if float(horse['track']) == 0:
                    horse['track'] = "{:.2f}".format(totalTrack/cntTotalTrack) if cntTotalTrack > 0 else "0"
                if float(horse['distance']) == 0:
                    horse['distance'] = "{:.2f}".format(totalDistance/cntTotalDistance) if cntTotalDistance > 0 else "0"
                if float(horse['condition']) == 0:
                    horse['condition'] = "{:.2f}".format(totalCondition/cntTotalCondition) if cntTotalCondition > 0 else "0"
                if float(horse['placePercent']) == 0:
                    horse['placePercent'] = "{:.2f}".format(totalPlace/cntTotalPlace) if cntTotalPlace > 0 else "0"
                if float(horse['winPercent']) == 0:
                    horse['winPercent'] = "{:.2f}".format(totalWin/cntTotalWin) if cntTotalWin > 0 else "0"
                if float(horse['finishPercent']) == 0:
                    horse['finishPercent'] = "{:.2f}".format(totalFinish/cntTotalFinish) if cntTotalFinish > 0 else "0"
                if float(horse['average']) == 0:
                    horse['average'] = "{:.2f}".format(totalAvg/cntTotalAvg) if cntTotalAvg > 0 else "0"
                if float(horse['class']) == 0:
                    horse['class'] = "{:.2f}".format(totalClass/cntTotalClass) if cntTotalClass > 0 else "0"
            tmpHorses.append (horse)
        
        rlt['horses'] =  horses
        return rlt

    def getRaceHorseScores(self, dateStr, trackName, raceNum, condition="Good", marketId=""):
        data = self.getRankHorse(dateStr, trackName, raceNum, condition, marketId)
        data = pd.DataFrame(data, columns=['Horse Name', 'Career Strike Rate', 'Career Place Strike Rate', 'Average Prize Money', 'This Track Strike Rate', 'This Track Place Strike Rate',
                                        'This Distance Strike Rate', 'This Distance Place Strike Rate', 'This Condition Strike Rate','This Condition Place Strike Rate',
                                        'Jockey Last 100 Strike Rate','Jockey Last 100 Place Strike Rate','Trainer Last 100 Strike Rate','Trainer Last 100 Place Strike Rate',
                                        'Weight Carried','Barrier','Last Start Finish Position','Last Start Margin'])
        # List of metrics where higher values are better
        higher_is_better = [
            'Career Strike Rate',
            'Career Place Strike Rate',
            'Average Prize Money',
            'This Track Strike Rate',
            'This Track Place Strike Rate',
            'This Distance Strike Rate',
            'This Distance Place Strike Rate',
            'This Condition Strike Rate',
            'This Condition Place Strike Rate',
            'Jockey Last 100 Strike Rate',
            'Jockey Last 100 Place Strike Rate',
            'Trainer Last 100 Strike Rate',
            'Trainer Last 100 Place Strike Rate'
        ]
        # Normalizing the metrics where higher values are better
        for col in higher_is_better:
            data[col] = (data[col] - data[col].min()) / (data[col].max() - data[col].min())
        # List of metrics where lower values are better
        lower_is_better = [
            'Weight Carried',
            'Barrier',
            'Last Start Finish Position',
            'Last Start Margin'
        ]

        # Normalizing the metrics where lower values are better
        for col in lower_is_better:
            data[col] = 1 - (data[col] - data[col].min()) / (data[col].max() - data[col].min())

        # Combining the metrics with equal weighting to generate a composite score
        weighted_cols = higher_is_better + lower_is_better
        data['Composite Score'] = data[weighted_cols].mean(axis=1)

        # Rescaling the composite scores to be within the 1-10 range
        min_score = data['Composite Score'].min()
        max_score = data['Composite Score'].max()
        data['Composite Score'] = 1 + 9 * (data['Composite Score'] - min_score) / (max_score - min_score)

        # Sorting the horses based on their composite scores
        return data.set_index('Horse Name')['Composite Score'].to_dict()


    def getRankHorse(self, dateStr, trackName, raceNum, condition="Good", marketId=""):
        races = dbManager.raceCol.getMainRaceByNum(datetime.strptime(dateStr, "%Y-%m-%d"), trackName, raceNum)

        if races is None or (races is not None and len(list(races)) == 0):
            return None

        market = dbManager.eventCol.getMarketByNum(marketId)
        runners = []
        if market is not None:
            marketBook = dbManager.marketBookCol.getRecentMarketBookById(market["marketId"])
            if marketBook is not None:
                tmpRunners = []
                for runner in marketBook['runners']:
                    if runner['status'].upper() != 'REMOVED': tmpRunners.append(runner['selectionId'])
                for runner in market['runners']:
                    if runner['selectionId'] in tmpRunners:
                        pams = runner['runnerName'].split(" ")
                        name = runner['runnerName'][len(pams[0]) + 1:]
                        runners.append (int(pams[0][:-1]))
        
        def sortFunc(race):
            return race['date'].timestamp()
        
        data = []
        for race in races:
            race = dict(race)
            if len(runners) > 0 and 'tab_no' in race and int(race['tab_no']) not in runners:
                continue
            # horse = dbManager.horseCol.getHorseById (int(race['horse_id']))
            horseRaces = dbManager.raceCol.getRacesByHorseId(datetime.strptime(dateStr, "%Y-%m-%d"), trackName, raceNum, int(race['horse_id']))
            # horse = dict (horse)
            # if 'races' not in horse: horse['races'] = []
            careerRuns = 0; careerWins = 0; careerPlaces = 0
            sumPrize = 0
            thisTrackRuns = 0; thisTrackWins = 0; thisTrackPlaces = 0
            thisDistanceRuns = 0; thisDistanceWins = 0; thisDistancePlaces = 0
            thisCondRuns = 0; thisCondWins = 0; thisCondPlaces = 0
            lastR = None; startDate = datetime.strptime("1970/01/01", "%Y/%m/%d")
            # if 'races' not in horse: horse['races'] = []
            for r in horseRaces:
                r = dict (r)
                
                if "trial" in r['class'].lower(): continue

                careerRuns += 1
                if int(r['finish_number']) == 1: careerWins += 1
                if int(r['finish_number']) < 4: careerPlaces += 1
                if 'horse_prizemoney' in r: sumPrize += r['horse_prizemoney']
                if 'horse_prizemoney_bonus' in r: sumPrize += r['horse_prizemoney_bonus']
                if ('home_id_name' in r and int(r['track_id']) == int(r['home_id_name'])) or ('home_track_id' in r and int(r['track_id']) == int(r['home_track_id'])):
                    thisTrackRuns += 1
                    if int(r['finish_number']) == 1: thisTrackWins += 1
                    if int(r['finish_number']) < 4: thisTrackPlaces += 1
                if math.ceil(int(r['distance'])/100) * 100 == math.ceil(int(race['distance'])/100) * 100:
                    thisDistanceRuns += 1
                    if int(r['finish_number']) == 1: thisDistanceWins += 1
                    if int(r['finish_number']) < 4: thisDistancePlaces += 1
                if 'track_condition' in r and condition.upper() == r['track_condition'].upper():
                    thisCondRuns += 1
                    if int(r['finish_number']) == 1: thisCondWins += 1
                    if int(r['finish_number']) < 4: thisCondPlaces += 1
                try:
                    if startDate < r['date']:
                        startDate = r['date']
                        lastR = r
                except:
                    pass
            careerStrikeRate = careerWins * 100 / careerRuns if careerRuns > 0 else 0
            careerStrikePlaceRate = careerPlaces * 100 / careerRuns if careerRuns > 0 else 0
            averagePrize = sumPrize / careerRuns if careerRuns > 0 else 0
            thisTrackStrikeRate = thisTrackWins * 100 / thisTrackRuns if thisTrackRuns > 0 else 0
            thisTrackStrikePlaceRate = thisTrackPlaces * 100 / thisTrackRuns if thisTrackRuns > 0 else 0
            thisDistanceStrikeRate = thisDistanceWins * 100 / thisDistanceRuns if thisDistanceRuns > 0 else 0
            thisDistanceStrikePlaceRate = thisDistancePlaces * 100 / thisDistanceRuns if thisDistanceRuns > 0 else 0
            thisCondStrikeRate = thisCondWins * 100 / thisCondRuns if thisCondRuns > 0 else 0
            thisCondStrikePlaceRate = thisCondPlaces * 100 / thisCondRuns if thisCondRuns > 0 else 0

            trainerLast100StrikeRate = 0; trainerLast100StrikePlaceRate = 0
            jockeyLast100StrikeRate = 0; jockeyLast100StrikePlaceRate = 0
            trainer = dbManager.trainerCol.getTrainerById (int(race['main_trainer_id']))
            trainer = dict (trainer) if trainer is not None else {}
            if 'races' in trainer:
                lastWins = 0; lastPlaces = 0; cnt = 0
                trainer['races'].sort(key=sortFunc, reverse=True)
                for trace in trainer['races']:
                    if cnt > 99: break
                    if "trial" in trace['class'].lower(): continue
                    cnt += 1
                    if int(trace['finish_number']) == 1: lastWins += 1
                    if int(trace['finish_number']) < 4: lastPlaces += 1
                trainerLast100StrikeRate = lastWins * 100 / min(100, cnt) if cnt > 0 else 0
                trainerLast100StrikePlaceRate = lastPlaces * 100 / min(100, cnt) if cnt > 0 else 0
            jockey = dbManager.jockeyCol.getJockeyById (int(race['main_jockey_id']))
            jockey = dict (jockey) if jockey is not None else {}
            if 'races' in jockey:
                lastWins = 0; lastPlaces = 0; cnt = 0
                jockey['races'].sort(key=sortFunc, reverse=True)
                for jrace in jockey['races']:
                    if cnt > 99: break
                    if "trial" in jrace['class'].lower(): continue
                    cnt += 1
                    if int(jrace['finish_number']) == 1: lastWins += 1
                    if int(jrace['finish_number']) < 4: lastPlaces += 1
                jockeyLast100StrikeRate = lastWins * 100 / min(100, cnt)
                jockeyLast100StrikePlaceRate = lastPlaces * 100 / min(100, cnt)
            
            barrier = int(race['horse_barrier']) if 'horse_barrier' in race else 0
            weightCarried = float(race['weight_total']) if 'weight_total' in race else 0
            lastFn = int(lastR['finish_number']) if lastR is not None else 0
            lastMgn = float(lastR['margin']) if lastR is not None else 0

            data.append ([race['horse_name'], careerStrikeRate, careerStrikePlaceRate, averagePrize, thisTrackStrikeRate, thisTrackStrikePlaceRate, 
                            thisDistanceStrikeRate, thisDistanceStrikePlaceRate, thisCondStrikeRate, thisCondStrikePlaceRate,
                            jockeyLast100StrikeRate, jockeyLast100StrikePlaceRate, trainerLast100StrikeRate, trainerLast100StrikePlaceRate,
                            weightCarried, barrier, lastFn, lastMgn])
        return data
    
    def getJockeyNames(self, marketId):
        eventObj = dbManager.eventCol.getDocumentsByMarketId (marketId)
        eventObj = eventObj[0]
        rlt_market = None
        for market in eventObj['markets']:
            if market['marketId'] == marketId:
                rlt_market = market
                break
        rlt = {}
        for runner in rlt_market['runners']:
            pams = runner['runnerName'].split(" ")
            rlt[pams[0][:-1]] = runner['metadata']['JOCKEY_NAME'] if 'metadata' in runner and 'JOCKEY_NAME' in runner['metadata'] else ''
        return rlt
    
    def setCondition(self, dateStr, trackName, raceNum, condition="Soft"):
        rlt = dbManager.raceCol.setConditionOnMainRace(datetime.strptime(dateStr, "%Y-%m-%d"), trackName, raceNum, condition)
        return rlt