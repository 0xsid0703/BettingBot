import sys
sys.path.append ("..")
from utils.logging import colManagerLogger
from utils.constants import KEY_NAME, TRACKS

class ColManager:
    def __init__(self, database, colName):
        if database is None:
            colManagerLogger.error ("database object is None.")
            return None
        if colName is None or len(colName.strip()) == 0:
            colManagerLogger.error ("Collection Name is None or empty.")
            return None
        self.database = database
        self.colName = colName
        try:
            self.manager = self.database [self.colName]
        except Exception as e:
            colManagerLogger.error ("%s collection calling failed" % colName, exc_info=True)
    
    def insertMany (self, dList):
        return self.manager.insert_many (dList)

    # Use in only trainer, jockey, horse model
    def getRecordsByFilter(self, filter):
        try:
            pipeline = []
            matchObj = {}
            project = {
                "name": 1,
                "id": 1,
                'races': {
                    '$filter': {
                        'input': '$races',
                        'as': 'item',
                        'cond': {
                            '$and': []
                        }
                    }
                }
            }
            for key in list(filter.keys()):
                if key == "jockey" or key == "trainer" or key == "horse" or key == "condition":
                    if filter[key].startswith("ALL "): continue
                    matchObj["races." + KEY_NAME[key]] = filter[key]
                    project['races']['$filter']['cond']['$and'].append ({
                        "$eq": ["$$item." + KEY_NAME[key], filter[key]]
                    })
            
            if filter['distance'] == "1000 - 1200":
                matchObj["races.distance"] = {"$gte": 1000, "$lte": 1200}
                project['races']['$filter']['cond']['$and'].append ({
                        "$gte": ["$$item.distance", 1000]
                })
                project['races']['$filter']['cond']['$and'].append ({
                        "$lte": ["$$item.distance", 1200]
                })
            elif filter['distance'] == "1300 - 1600":
                matchObj["races.distance"] = {"$gte": 1300, "$lte": 1600}
                project['races']['$filter']['cond']['$and'].append ({
                        "$gte": ["$$item.distance", 1300]
                })
                project['races']['$filter']['cond']['$and'].append ({
                        "$lte": ["$$item.distance", 1600]
                })
            elif filter['distance'] == "1800 - 2200":
                matchObj["races.distance"] = {"$gte": 1800, "$lte": 2200}
                project['races']['$filter']['cond']['$and'].append ({
                        "$gte": ["$$item.distance", 1800]
                })
                project['races']['$filter']['cond']['$and'].append ({
                        "$lte": ["$$item.distance", 2200]
                })
            elif filter['distance'] == "2400+":
                matchObj["races.distance"] = {"$gte": 2400}
                project['races']['$filter']['cond']['$and'].append ({
                        "$gte": ["$$item.distance", 2400]
                })
            
            [tk, tv] = filter['track']
            tracks = TRACKS.copy ()
            tAll = tracks[tk]["METRO"] + tracks[tk]["PROVINCIAL"] + tracks[tk]["COUNTRY"]
            tracks[tk]['ALL'] = tAll
            
            matchObj["races.track_name"] = {"$in": tracks[tk][tv]}
            project['races']['$filter']['cond']['$and'].append ({
                        "$in": ["$$item.track_name", tracks[tk][tv]]
            })

            # if filter['start'] != "This Season" and filter['start'] != "Last Season":

            pipeline.append ({"$match": matchObj})
            pipeline.append ({"$project": project})

            return self.manager.aggregate (pipeline)
        except:
            colManagerLogger.error ("%s collection calling failed" % self.colName, exc_info=True)
            return []