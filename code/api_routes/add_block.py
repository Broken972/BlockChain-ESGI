from flask import jsonify,request
import json
import os,hashlib
from datetime import datetime
from flask_jwt_extended import jwt_required
import threading
import sys
sys.path.insert(0, '..')

from functions import *

@jwt_required()
def add_block():
    request_data = request.get_json()
    try:
       request_data['status']
       request_data['product_name']
       request_data['product_location']
       request_data['product_destination']
       request_data['packages_total_number']
       request_data['packages_total_weight']
       request_data['package_id']
       request_data['product_detail']
    except:
        return jsonify({'Status': 'Error', 'Cause': 'A mendatory field was not defined'}), 400
    try:
        with open("blockchain_data.json", "r") as file:
            chain = json.load(file)
            last_block_hash = chain[-1]['block_hash']
            current_datetime = datetime.now()
            time=current_datetime.strftime("%Y-%m-%d|%H:%M:%S.%f")[:23]
            new_data = {
                "previous_block_hash": last_block_hash,
                "time": time,
                "status": request_data['status'],
                "produit": request_data['product_name'],
                "current_place": request_data['product_location'],
                "destination": request_data['product_destination'],
                "packages_total_number": request_data['packages_total_number'],
                "packages_total_weight": request_data['packages_total_weight'],
                "package_id": request_data['package_id'],
                "product_detail": request_data['product_detail'],
                "product_family": request_data["product_family"],
                "product_current_owner": request_data["product_current_owner"],
                "product_origin_country": request_data["product_origin_country"],
                "product_origin_producer": request_data["product_origin_producer"]
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
        return jsonify({'Status': 'Success'}), 200
    except Exception as e:
        return jsonify({'Status': 'Error', "msg": str(e)}), 500