import asyncio
import datetime
import websockets
import json

from controllers.boardController import BoardController

boardController = BoardController()

async def handler(websocket, path):
    try:
        message = await websocket.recv()
        print (message, "DDDDDD")
        data = json.loads(message)
        startDate = data['startDate'] if 'startDate' in data else None
        venue = data['venue'] if 'venue' in data else None
        raceNum = data['raceNum'] if 'raceNum' in data else None
        marketId = data['marketId'] if 'marketId' in data else None
        
        if startDate is not None and venue is not None and raceNum is not None and marketId is not None:
            while True:
                raceCard = boardController.getRaceCardByNum (startDate, venue, raceNum, None, marketId)
                raceForm = boardController.getRaceFormByNum (startDate, venue, raceNum, None, marketId)
                await websocket.send (json.dumps({"raceCard": raceCard, "raceForm": raceForm}))
                await asyncio.sleep(3)
    except Exception as e:
        pass

start_server = websockets.serve(handler, "0.0.0.0", 5556)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()