# logging customize
from os import path
import logging
import logging.config

logConfig = path.join(path.dirname(path.dirname(path.abspath(__file__))),'config/logging.conf')
logging.config.fileConfig(logConfig, disable_existing_loggers=False)

daemonLogger = logging.getLogger("daemon.py")
streamLogger = logging.getLogger("stream.py")
tradingLogger = logging.getLogger("betfairs/trading")
basicControllerLogger = logging.getLogger("controllers/basicConttroller")
profileControllerLogger = logging.getLogger("controllers/profileConttroller")
boardControllerLogger = logging.getLogger("controllers/boardConttroller")
dbLogger = logging.getLogger("models/dbManager")
colManagerLogger = logging.getLogger("models/colManager")
eventLogger = logging.getLogger("models/event")
marketBookLogger = logging.getLogger("models/marketBook")
marketIdsLogger = logging.getLogger("models/marketIds")
trackLogger = logging.getLogger("models/track")
trainerLogger = logging.getLogger("models/trainer")
jockeyLogger = logging.getLogger("models/jockey")
horseLogger = logging.getLogger("models/horse")
raceLogger = logging.getLogger("models/race")
algoLogger = logging.getLogger("prompts/algo")
utilsLogger = logging.getLogger("utils")