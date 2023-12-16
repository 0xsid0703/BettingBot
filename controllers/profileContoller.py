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
            try:
                horse = dbManager.horseCol.getHorseById(id)
                rlt  = []
                for race in horse['races']:
                    race = dict(race)
                    if 'barrier' in race['class'].lower(): continue
                    race['_id'] = str(race['_id'])
                    race['horse_foaling_date'] = race['horse_foaling_date'].strftime("%d/%m/%y") if 'horse_foaling_date' in race else ''
                    race['date'] = race['date'].strftime("%d/%m/%y") if 'date' in race else ''
                    race['home_date'] = race['home_date'].strftime("%d/%m/%y") if 'home_date' in race else ''
                    rlt.append (race)
                return rlt
            except:
                return []
        
        if type == "trainer":
            try:
                trainer = dbManager.trainerCol.getTrainerById(id)
                rlt  = []
                for race in trainer['races']:
                    if 'barrier' in race['class'].lower(): continue
                    race['_id'] = str(race['_id'])
                    race['horse_foaling_date'] = race['horse_foaling_date'].strftime("%d/%m/%y")
                    race['date'] = race['date'].strftime("%d/%m/%y")
                    race['home_date'] = race['home_date'].strftime("%d/%m/%y") if 'home_date' in race else ''

                    rlt.append (race)
                return rlt
            except:
                return []
        
        if type == "jockey":
            try:
                jockcey = dbManager.jockeyCol.getJockeyById(id)
                rlt  = []
                for race in jockcey['races']:
                    if 'barrier' in race['class'].lower(): continue
                    race['_id'] = str(race['_id'])
                    race['horse_foaling_date'] = race['horse_foaling_date'].strftime("%d/%m/%y")
                    race['date'] = race['date'].strftime("%d/%m/%y")
                    race['home_date'] = race['home_date'].strftime("%d/%m/%y") if 'home_date' in race else ''

                    rlt.append (race)
                return rlt
            except:
                return []