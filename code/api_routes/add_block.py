import json
import os,hashlib
from datetime import datetime
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
import threading,asyncio
import aiofiles
from listeners.fast_stream_config import faststream_app, broker,node_queue,global_new_block_exch
from functions.tailscale_functions import *
import random
import sys
sys.path.insert(0, '..')

from functions import *
from functions import *
from functions import *
from functions.blockchain_functions import *
from functions.consul.find_available_services import *
from functions.rabbitmq_functions import *
app = FastAPI()
async def read_chain():
    async with aiofiles.open("blockchain_data.json", "r") as file:
        contents = await file.read()
        return json.loads(contents)

async def write_chain(chain):
    async with aiofiles.open("blockchain_data.json", "w") as file:
        await file.write(json.dumps(chain, indent=4))

async def add_block(user_data, Authorize,healthy_nodes):
    Authorize.jwt_required()
    try:
        chain = await read_chain()
        last_block_hash = chain[-1]['block_hash']
        current_datetime = datetime.now()
        time = current_datetime.strftime("%Y-%m-%d|%H:%M:%S.%f")[:23].replace('"','')
        if len(user_data.secret_data) != 0 and len(user_data.secret_data_receiver) != 0:
            user_pub_key = get_public_key_by_name(Authorize.get_jwt_subject())
            print(user_pub_key)
            encrypted_msg = cipher_msg_with_pub_key(str(user_data.secret_data),user_pub_key)
        new_data = {
            "previous_block_hash": last_block_hash,
            "time": time,
            "status": user_data.status,
            "product_name": user_data.product_name,
            "product_location": user_data.product_location,
            "product_destination": user_data.product_destination,
            "packages_total_number": user_data.packages_total_number,
            "packages_total_weight": user_data.packages_total_weight,
            "package_id": user_data.package_id,
            "product_detail": user_data.product_detail,
            "product_family": user_data.product_family,
            "product_current_owner": Authorize.get_jwt_subject(),
            "product_origin_country": user_data.product_origin_country,
            "product_origin_producer": user_data.product_origin_producer,
            "secret_data": encrypted_msg,
            "secret_data_receiver": user_data.secret_data_receiver
        }
        json_string = json.dumps(new_data, sort_keys=True)
        encoded_data = json_string.encode()
        # Create a SHA-256 hash of the encoded bytes
        hash_object = hashlib.sha256(encoded_data)
        hash_hex = hash_object.hexdigest()
        new_data["block_hash"] = hash_hex
        chain.append(new_data)
        #await write_chain(chain)
        if "true" not in os.getenv("VALIDATOR_NODE"):
            our_node = return_current_tailscale_domains()[0]
            validators = await get_healthy_services('blockchain-server',our_node,"validator")
            random_validator = random.choice(validators)
            jwt = obtain_jwt_from_remote(f"{random_validator}:5000")
            print(jwt)
            if "error" not in jwt:
                url = f'https://{random_validator}:5000/validate_block'
                headers = {
                    'Content-Type': "application/json",
                    'Authorization': f'Bearer {jwt}'
                }
                response = requests.post(url, headers=headers, json=new_data)
                print(response.status_code)
                if response.status_code == 200:
                    validator_signature = response.json()['signature']
                    new_data["validator_signature"] = validator_signature
                    print("received signature" + validator_signature)
                    await broker.connect()
                    print(await broker.publish(new_data, exchange=global_new_block_exch))
                    return "success"
                else:
                    return "ko"
            else:
                return "ko"
        else:
            new_data["validator_signature"] = generate_signature().decode()
            await broker.connect()
            print(await broker.publish(new_data, exchange=global_new_block_exch))
            return "success"
    except Exception as e:
        print(e)
        return "ko"
