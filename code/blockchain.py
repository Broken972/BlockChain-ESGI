import hashlib
import json
import sys
from fastapi import FastAPI, Request, Depends, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
import os
from pydantic import BaseModel
import uvicorn
import time
import asyncio

# Import API Routes
from api_routes.health import health_function
from api_routes.is_jwt_valid import is_jwt_valid
from api_routes.add_block import add_block
from api_routes.keys_list import keys_list
from api_routes.blockchain_list import blockchain_list
from api_routes.auth_api import auth_api
from api_routes.jwks import jwks_function

# Import functions
from functions.rabbitmq_functions import *
from functions.tailscale_functions import *
from functions.blockchain_functions import *

# Import listeners
from listeners.validator_receiver import start_rabbitmq_consumer

# Messages de réponse pour l'authentification
auth_failed = {"status": "error", "message": "Authentication failed"}
auth_succeed = {"status": "success", "message": "Authenticated successfully"}

# Indicateur si le node actuel est un node de démarrage (bootstrap)
is_bootstrap_node = True

# Informations globales sur les clés publiques et la chaîne de blocs
global public_keys, chain

# Initialisation de l'application FastAPI
app = FastAPI()

# Load RSA keys
with open('./keys/private_key.pem', 'r') as f:
    private_key = f.read()
with open('./keys/public_key.pem', 'r') as f:
    public_key = f.read()

# Configure FastAPI-JWT-Auth
class Settings(BaseModel):
    authjwt_algorithm: str = "RS256"
    authjwt_private_key: str = private_key
    authjwt_public_key: str = public_key
    authjwt_secret_key: str = os.getenv("JWT_SECRET_KEY")
    authjwt_decode_audience: str = "rabbitmq"

class AddBlock(BaseModel):
    status: str
    product_name: str
    product_location: str
    product_destination: str
    packages_total_number:str
    packages_total_weight: str
    package_id: str
    product_detail: str
    product_family: str
    product_current_owner: str
    product_origin_country: str
    product_origin_producer: str

@AuthJWT.load_config
def get_config():
    return Settings()

# Création des routes
@app.get('/health')
async def health():
    return await health_function()

@app.get('/is_jwt_valid')
async def is_jwt_valid_fast():
    return await is_jwt_valid()

@app.post('/add_block')
async def add_block_fast(user_data: AddBlock,Authorize: AuthJWT = Depends()):
    return await add_block(user_data,Authorize)

@app.get('/keys_list')
async def keys_list_fast():
    return await keys_list()

@app.get('/blockchain_list')
async def blockchain_list_fast():
    return await blockchain_list()

@app.post('/auth_api')
async def auth_api_fast(public_key: str = Form(...), signature: str = Form(...),Authorize: AuthJWT = Depends()):
    return await auth_api(public_key,signature,Authorize)

@app.get('/.well-known/jwks.json')
async def jwks(request: Request):
    return await jwks_function(request)

# Point d'entrée principal pour l'exécution de l'application
if __name__ == "__main__":
    time.sleep(5)
    
    async def main():
        try:
            our_domain, our_short_domain = return_current_tailscale_domains()
            print(f"[*] Acquired tailscale IP : {our_domain}")
        except:
            print("[ERROR] : Impossible to acquire tailscale IP stopping...")
            sys.exit()
        params = rabbit_create_local_connections_parameters()
        if params == False:
            print("[ERROR] : Impossible to create local connections parameters to rabbitmq stopping here....")
            sys.exit()
        print("[*] Created local parameters")
        own_queue = rabbit_create_own_node_queue(params, "receive_block")
        if own_queue == False:
            print("[ERROR] : Impossible to create local queue stopping here....")
            sys.exit()
        if 'true' in os.getenv("VALIDATOR_NODE"):
            validator_queue = rabbit_create_own_node_queue(params, "validate_block")
        print("[*] Created local queue(s)")
        while True:
            try:
                load_blockchain_data()
            except Exception as e:
                print(f"[!] Error loading local blockchain : {e}")
            try:
                public_keys = load_verified_public_keys()
            except Exception as e:
                print(f"[!] Error loading local public_keys  : {e}")
            break
        print("[*] Noeud lancé")
    #asyncio.run(main())
    #uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get('LISTEN_PORT', 5000)), ssl_keyfile='./keys/node_tls.key', ssl_certfile='./keys/node_tls.crt')
