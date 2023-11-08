from flask_restx import Api

from .basic import api as basic
from .profile import api as profile
from .board import api as board

api = Api(
    title='Horse Racing in Betfair Application',
    version='1.0',
    description='Horse Racing in Betfair Application',
    # All API metadatas
)

api.add_namespace(basic)
api.add_namespace(profile)
api.add_namespace(board)