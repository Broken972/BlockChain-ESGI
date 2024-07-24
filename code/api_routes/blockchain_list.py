import sys
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
sys.path.insert(0, '..')

from functions.blockchain_functions import *

# Route Flask pour obtenir la liste des blocs de la blockchain
async def blockchain_list():
    chain = load_blockchain_data()
    return chain