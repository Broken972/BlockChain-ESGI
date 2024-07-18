from fastapi import FastAPI, Depends,Form
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
import sys
sys.path.insert(0, '..')

from functions.blockchain_functions import authenticate_api
from functions.blockchain_functions import load_verified_public_keys
async def auth_api(client_public_key,client_signature,Authorize):
    print(client_public_key,client_signature)
    if client_public_key is None:
        return JSONResponse(content={'Error': 'No public key provided'}, status_code=400)
    if client_signature is None:
        return JSONResponse(content={'Error': 'No signature provided'}, status_code=400)
    token = authenticate_api(client_public_key, client_signature, load_verified_public_keys(),Authorize)
    if token != False:
        return JSONResponse(content={'Token:': token}, status_code=200)
    else:
        return JSONResponse(content={'status': 'error','msg': 'Unauthorized'}, status_code=400)