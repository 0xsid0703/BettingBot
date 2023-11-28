from mongoengine import *
import datetime
from .colManager import ColManager

import sys
sys.path.append ("..")
from utils.logging import horseLogger

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
    