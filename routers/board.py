import sys
from flask_restx import Namespace, Resource, reqparse
from flask import request

api = Namespace('api/board', description='LeaderBoard controllers')

sys.path.append("..")
from controllers.boardController import BoardController

boardController = BoardController()

parser = reqparse.RequestParser()
parser.add_argument('filter', location='json', type=dict)
parser.add_argument('kind', location='json', type=str)
parser.add_argument('page', location='json', type=int)
parser.add_argument('sortedCol', location='json', type=str)
parser.add_argument('sortDirection', location='json', type=int)

@api.route ('/getrecords')
class RaceHoseList(Resource):
    def post(self):
        filter = parser.parse_args()['filter']
        kind = parser.parse_args()['kind']
        page = parser.parse_args()['page']
        sortedCol = parser.parse_args()['sortedCol']
        sortDirection = parser.parse_args()['sortDirection']
        return boardController.getLeaderBoards (filter, kind, page, sortedCol, sortDirection)

@api.route ('/gettrainernames')
class TrainerNameList(Resource):
    def get(self):
        name = request.args.get("name")
        return boardController.getTrainernames (name)

@api.route ('/gethorsenames')
class HorseNameList(Resource):
    def get(self):
        name = request.args.get("name")
        return boardController.getHorsenames (name)

@api.route ('/getjockeynames')
class JockeyNameList(Resource):
    def get(self):
        name = request.args.get("name")
        return boardController.getJockeynames (name)