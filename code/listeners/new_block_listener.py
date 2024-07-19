from listeners.fast_stream_config import faststream_app, broker,node_queue,global_new_block_exch
from faststream import FastStream, Logger
from functions.blockchain_functions import find_matching_key,load_verified_public_keys,extract_public_keys
import json
@broker.subscriber(node_queue, global_new_block_exch)
async def handle_message(msg, logger: Logger):
    logger.info(f"Received message: {msg}")
    if type(msg) == bytes:
        msg=msg.decode()
    validator_signature=msg['validator_signature']
    logger.info(f"Received signature: {validator_signature}")
    verified_keys = load_verified_public_keys()
    matching_key = find_matching_key(verified_keys, b"valid_block", validator_signature)
    if matching_key:
        print(f"The signature matches the public key of: {matching_key}")
        pub_keys_info = extract_public_keys(verified_keys)
        for identity in pub_keys_info:
            if identity["name"] == matching_key:
                is_signature_of_validator = identity["is_validator"]
                if is_signature_of_validator:
                    logger.info(f"{matching_key} is a validator")
                else:
                    logger.info(f"{matching_key} is not a validator")
    else:
        print("No matching public key found for the signature.")