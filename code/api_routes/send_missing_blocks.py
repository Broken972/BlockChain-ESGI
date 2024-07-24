from fastapi import FastAPI, Depends,Form
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
import sys
sys.path.insert(0, '..')

from functions.find_missing_blocks import *
async def send_missing_blocks(latest_hash,Authorize):
    Authorize.jwt_required()
    print(latest_hash)
    blockchain=load_blockchain_data()
    missing_blocks = []
    subsequent_blocks = get_subsequent_blocks(blockchain, latest_hash)
    for block in subsequent_blocks:
        print(block)
        missing_blocks.append(block)
    if len(missing_blocks) != 0:
        return subsequent_blocks
    else:
        return "up to date"