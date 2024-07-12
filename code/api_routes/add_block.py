import json
import os,hashlib
from datetime import datetime
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
import threading
import sys
sys.path.insert(0, '..')

from functions import *
app = FastAPI()
async def add_block(user_data,Authorize):
    Authorize.jwt_required()
    try:
        with open("blockchain_data.json", "r") as file:
            chain = json.load(file)
            last_block_hash = chain[-1]['block_hash']
            current_datetime = datetime.now()
            time=current_datetime.strftime("%Y-%m-%d|%H:%M:%S.%f")[:23]
            new_data = {
                "previous_block_hash": last_block_hash,
                "time": time,
                "status": user_data.status,
                "produit": user_data.product_name,
                "current_place": user_data.product_location,
                "destination": user_data.product_destination,
                "packages_total_number": user_data.packages_total_number,
                "packages_total_weight": user_data.packages_total_weight,
                "package_id": user_data.package_id,
                "product_detail": user_data.product_detail,
                "product_family": user_data.product_family,
                "product_current_owner": user_data.product_current_owner,
                "product_origin_country": user_data.product_origin_country,
                "product_origin_producer": user_data.product_origin_producer,
            }
            json_string = json.dumps(new_data, sort_keys=True)
            encoded_data = json_string.encode()
            # Create a SHA-256 hash of the encoded bytes
            hash_object = hashlib.sha256(encoded_data)
            hash_hex = hash_object.hexdigest()
            new_data["block_hash"] = hash_hex
            chain.append(new_data)
            with open("blockchain_data.json", "w") as file:
                json.dump(chain, file, indent=4)
        return JSONResponse(content={'Status': 'Success'}, status_code=200)
    except Exception as e:
        return JSONResponse(content={'Status': 'Error','msg': e}, status_code=500)