import json
import os,hashlib
from datetime import datetime
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
import threading,asyncio
import sys
sys.path.insert(0, '..')

from functions import *
from functions import *
from functions import *
from functions.blockchain_functions import *
from functions.consul.find_available_services import *
from functions.rabbitmq_functions import *
from functions.tailscale_functions import *

app = FastAPI()

def validate_json(json_data, required_keys):
    try:
        json_data = json.loads(json_data)
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON format: {e}"
    for key in required_keys:
        if key not in json_data:
            return False, f"Missing required key: {key}"
        if not isinstance(json_data[key], str) or not json_data[key].strip():
            return False, f"Invalid or empty value for key: {key}"
    status_value = json_data.get('status', '').strip().lower()
    if status_value not in ['valide', 'invalide']:
        return False, 'Invalid value for key: status. Must be "Valide" or "Invalide" (case insensitive)'
    return True, "All required keys are present with valid string values"

async def validate_block(user_data_to_validate,Authorize,healthy_nodes):
    Authorize.jwt_required()
    new_data = {
        "previous_block_hash": user_data_to_validate.previous_block_hash,
        "time": user_data_to_validate.time,
        "status": user_data_to_validate.status,
        "produit": user_data_to_validate.product_name,
        "current_place": user_data_to_validate.product_location,
        "destination": user_data_to_validate.product_destination,
        "packages_total_number": user_data_to_validate.packages_total_number,
        "packages_total_weight": user_data_to_validate.packages_total_weight,
        "package_id": user_data_to_validate.package_id,
        "product_detail": user_data_to_validate.product_detail,
        "product_family": user_data_to_validate.product_family,
        "product_current_owner": user_data_to_validate.product_current_owner,
        "product_origin_country": user_data_to_validate.product_origin_country,
        "product_origin_producer": user_data_to_validate.product_origin_producer,
        "block_hash": user_data_to_validate.block_hash,
    }
    try:
        json_string = json.dumps(new_data, sort_keys=True)
    except Exception as e:
        return JSONResponse(content={'Status': 'Error','msg': e}, status_code=500)
    
    required_keys = [
        'previous_block_hash', 'time', 'status', 'produit', 'current_place', 
        'destination', 'packages_total_number', 'packages_total_weight', 
        'package_id', 'product_detail', 'product_family', 'product_current_owner', 
        'product_origin_country', 'product_origin_producer', 'block_hash'
    ]
    try:
        if validate_json(json_string,required_keys):
            return JSONResponse(content={'Status': 'Success',"signature": generate_signature().decode()}, status_code=200)
        else:
            return JSONResponse(content={'Status': 'Error','msg': e}, status_code=422)
    except Exception as e:
        return JSONResponse(content={'Status': 'Error','msg': e}, status_code=500)