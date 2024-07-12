from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import sys
import asyncio

# Insert the path to access custom functions
sys.path.insert(0, '..')

from functions.blockchain_functions import *
from functions.rabbitmq_functions import rabbit_check_health

app = FastAPI()
async def health_function():
    rabbit_health = rabbit_check_health()
    try:
        chain = await asyncio.to_thread(load_blockchain_data)
        public_keys = await asyncio.to_thread(load_verified_public_keys)
        merkle_root = await asyncio.to_thread(calculate_merkle_root_from_json, chain)
        return JSONResponse(content={
            'blockchain_status': 'Working as expected',
            "rabbitmq_status": rabbit_health[0],
            "rabbitmq_details": rabbit_health[1],
            "merkle_root": str(merkle_root)
        }, status_code=200)
    except Exception as error:
        print("[!] Impossible de récuperer les données nécessaires")
        return JSONResponse(content={
            'blockchain_status': f'Error {error}',
            "rabbitmq_status": rabbit_health[0],
            "rabbitmq_details": rabbit_health[1]
        }, status_code=500)