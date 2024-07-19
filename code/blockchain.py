import hashlib
import json
import sys
from fastapi import FastAPI, Request, Depends, HTTPException, Form,status
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
import os
from pydantic import BaseModel
import uvicorn
import time,re
import asyncio
from starlette.background import BackgroundTasks
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import logging
from faststream import FastStream, Logger

# Import API Routes
from api_routes.health import health_function
from api_routes.is_jwt_valid import is_jwt_valid
from api_routes.add_block import add_block
from api_routes.keys_list import keys_list
from api_routes.blockchain_list import blockchain_list
from api_routes.auth_api import auth_api
from api_routes.jwks import jwks_function
from api_routes.validate_block import validate_block

# Import functions
from functions.rabbitmq_functions import *
from functions.tailscale_functions import *
from functions.blockchain_functions import *
from functions.consul.find_available_services import *
from functions.consul.register_service import register_service

# Import listeners
from listeners.fast_stream_config import faststream_app, broker,node_queue,global_new_block_exch
import listeners.new_block_listener
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

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
	logging.error(f"{request}: {exc_str}")
	content = {'status_code': 10422, 'message': exc_str, 'data': None}
	return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

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

class ReceiveAddBlock(BaseModel):
    time: str
    previous_block_hash: str
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
    block_hash: str

# Start the FastStream application together with FastAPI
@app.on_event("startup")
async def startup_event():
    await faststream_app.start()
    await broker.connect()
    #Declare rabbitmq objects in case it does not exist
    await broker.declare_exchange(global_new_block_exch)
    await broker.close()


@app.on_event("shutdown")
async def shutdown_event():
    await faststream_app.stop()

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
    our_node = return_current_tailscale_domains()[0]
    healthy_nodes = await get_healthy_services('rabbitmq',our_node)
    print(healthy_nodes)
    return await add_block(user_data,Authorize,healthy_nodes)

@app.post('/validate_block')
async def validate_block_fast(user_data_to_validate: ReceiveAddBlock,Authorize: AuthJWT = Depends()):
    our_node = return_current_tailscale_domains()[0]
    healthy_nodes = await get_healthy_services('rabbitmq',our_node)
    print(healthy_nodes)
    return await validate_block(user_data_to_validate,Authorize,healthy_nodes)

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

@app.on_event("startup")
async def startup_event():
    our_node = return_current_tailscale_domains()[0]
    register_service(our_node,8501,"https","blockchain-server","blockchain-check", 5000, {"HTTP": "https://node-local-kali-2.tailc2844.ts.net:5000/health","Interval": "10s"})


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