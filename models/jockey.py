from mongoengine import *
import datetime
from .colManager import ColManager

import sys
sys.path.append ("..")
from utils.logging import jockeyLogger

class Jockey(ColManager):
    def __init__(self, database):
        super().__init__(database, "Jockey")
    
    def saveJockey(self, race_obj):
        try:
            jockey_count = self.manager.count_documents ({"id": race_obj['jockey_id']})
            if jockey_count > 0:
                jockeys = self.manager.count_documents ({"id": race_obj['jockey_id'], "races.track_id": race_obj['track_id'], "races.horse_id": race_obj['horse_id']})

                if jockeys > 0:
                    return

                jockeys = list(self.manager.find ({"id": race_obj['jockey_id']}))
                races = jockeys[0]['races']
                races.append (race_obj)
                self.manager.update_one(
                    {"id": race_obj['jockey_id']},
                    {"$set": {"id": race_obj['jockey_id'], "name": race_obj['jockey_name'], "races": races}}
                )
            else:
                self.manager.insert_one ({
                    "id": race_obj['jockey_id'],
                    "name": race_obj['jockey_name'],
                    "races": [race_obj]
                })
        except:
            jockeyLogger.error ("saveJockey() failed.", exc_info=True)

    def getAllJockeys(self, name):
        try:
            jockeys = self.manager.find ({"name": {"$regex" : name, "$options": "i"}})
            return jockeys
        except Exception as e:
            jockeyLogger.error ("getAllJockeys() failed.", exc_info=True)

    def getJockeyById(self, id):
        try:
            jockey = self.manager.find_one({"id": id})
            return jockey
        except:
            return None