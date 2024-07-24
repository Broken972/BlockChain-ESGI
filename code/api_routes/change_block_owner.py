from fastapi import FastAPI, Depends,Form
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from datetime import datetime
from listeners.fast_stream_config import faststream_app, broker,node_queue,global_new_block_exch
import sys
sys.path.insert(0, '..')

from functions.blockchain_functions import *
async def change_block_owner(block_hash,new_owner,Authorize):
    Authorize.jwt_required()
    latest_block = get_block_by_hash(block_hash)
    if latest_block:
        #return "Latest block with package ID {}: {}".format(package_id, latest_block)
        latest_block["product_current_owner"] = new_owner
        latest_block["time"] = datetime.now().strftime("%Y-%m-%d|%H:%M:%S.%f")[:23].replace('"','')
        json_string = json.dumps(latest_block, sort_keys=True)
        encoded_data = json_string.encode()
        latest_block["block_hash"] = hashlib.sha256(encoded_data).hexdigest()
        latest_block["previous_block_hash"] = get_latest_block()['block_hash']
        #return latest_block
        await broker.connect()
        print(await broker.publish(latest_block, exchange=global_new_block_exch))
        return "success"
    else:
        return "No block found with hash {}".format(block_hash)
