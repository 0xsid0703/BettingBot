import asyncio
import websockets
import json
import argparse
import os
from datetime import datetime
from controllers.boardController import BoardController

boardController = BoardController()

async def handler(websocket, path):
    try:
        message = await websocket.recv()
        data = json.loads(message)
        startDate = data['startDate'] if 'startDate' in data else None
        venue = data['venue'] if 'venue' in data else None
        raceNum = data['raceNum'] if 'raceNum' in data else None
        marketId = data['marketId'] if 'marketId' in data else None
        
        if startDate is not None and venue is not None and raceNum is not None and marketId is not None:
            while True:
                print (datetime.now().timestamp(), "================>")
                raceCard = boardController.getRaceCardByNum (startDate, venue, raceNum, None, marketId)
                raceForm = boardController.getRaceFormByNum (startDate, venue, raceNum, None, marketId)
                print (datetime.now().timestamp(), "================%")
                await websocket.send (json.dumps({"raceCard": raceCard, "raceForm": raceForm}))
                await asyncio.sleep(3)
    except Exception as e:
        pass

def main():

    parser = argparse.ArgumentParser(description="Horse Racing Server")
    parser.add_argument ("--start", help="RESP API Daemon Start", action="store_true")
    parser.add_argument ("--stop", help="RESP API Daemon Stop", action="store_true")
    args = parser.parse_args()

    if args.start:
        pid = os.fork()
        if pid > 0:
            fd = open("./socket-pid", "w"); fd.write (str(os.getpid())); fd.close()
            start_server = websockets.serve(handler, "0.0.0.0", 5556)
            asyncio.get_event_loop().run_until_complete(start_server)
            asyncio.get_event_loop().run_forever()
    
    elif args.stop:
        os.chdir(os.getcwd())
        fd = open ("./socket-pid", "r"); pid = fd.read(); fd.close()
        fd = os.popen ("kill %s" % pid.strip(), "r"); fd.close()



if __name__=="__main__":
    main ()