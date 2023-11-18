import betfairlightweight
from .controller import Controller
from datetime import datetime
import sys
sys.path.append('..')
from models.dbManager import dbManager
from utils.JSONEncoder import JSONEncoder
from utils.constants import *
from utils.logging import profileControllerLogger

class ProfileController(Controller):

    def __init__(self):
        super().__init__()
    
    def getRaceList(self, type, id):
        if type == "horse":
            races = dbManager.raceCol.getRacesByHorse(id)
            rlt  = []
            for race in races:
                race = dict(race)
                race['_id'] = str(race['_id'])
                race['horse_foaling_date'] = race['horse_foaling_date'].strftime("%d/%m/%y") if 'horse_foaling_date' in race else ''
                race['date'] = race['date'].strftime("%d/%m/%y") if 'date' in race else ''
                race['home_date'] = race['home_date'].strftime("%d/%m/%y") if 'home_date' in race else ''

                rlt.append (race)
            return rlt
        
        if type == "trainer":
            races = dbManager.raceCol.getRacesByTrainer(id)
            rlt  = []
            for race in races:
                race['_id'] = str(race['_id'])
                race['horse_foaling_date'] = race['horse_foaling_date'].strftime("%d/%m/%y")
                race['date'] = race['date'].strftime("%d/%m/%y")
                race['home_date'] = race['home_date'].strftime("%d/%m/%y") if 'home_date' in race else ''

                rlt.append (race)
            return rlt
        
        if type == "jockey":
            races = dbManager.raceCol.getRacesByJockey(id)
            rlt  = []
            for race in races:
                race['_id'] = str(race['_id'])
                race['horse_foaling_date'] = race['horse_foaling_date'].strftime("%d/%m/%y")
                race['date'] = race['date'].strftime("%d/%m/%y")
                race['home_date'] = race['home_date'].strftime("%d/%m/%y") if 'home_date' in race else ''

                rlt.append (race)
            return rlt