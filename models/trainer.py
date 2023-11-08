from mongoengine import *
import datetime
from .colManager import ColManager

import sys
sys.path.append ("..")
from utils.logging import trainerLogger

class Trainer(ColManager):
    def __init__(self, database):
        super().__init__(database, "Trainer")
    
    def saveTrainer(self, race_obj):
        try:
            trainer_count = self.manager.count_documents ({"id": race_obj['trainer_id']})
            if trainer_count > 0:
                trainers = self.manager.count_documents ({"id": race_obj['trainer_id'], "races.track_id": race_obj['track_id'], "races.horse_id": race_obj['horse_id']})

                if trainers > 0:
                    return

                trainers = list(self.manager.find ({"id": race_obj['trainer_id']}))
                races = trainers[0]['races']
                races.append (race_obj)
                self.manager.update_one(
                    {"id": race_obj['trainer_id']},
                    {"$set": {"id": race_obj['trainer_id'], "name": race_obj['trainer_name'], "races": races}}
                )
            else:
                self.manager.insert_one ({
                    "id": race_obj['trainer_id'],
                    "name": race_obj['trainer_name'],
                    "races": [race_obj]
                })
        except:
            trainerLogger.error ("saveTrainer() failed.", exc_info=True)

    def getAllTrainers(self, name):
        try:
            trainers = self.manager.find ({"name": {"$regex" : name, "$options": "i"}})
            return trainers
        except Exception as e:
            trainerLogger.error ("getAllTrainers() failed.", exc_info=True)
