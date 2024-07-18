from listeners.fast_stream_config import faststream_app, broker,node_queue,global_new_block_exch
from faststream import FastStream, Logger
import json
@broker.subscriber(node_queue, global_new_block_exch)
async def handle_message(msg, logger: Logger):
    logger.info(f"Received message: {msg}")
    if type(msg) != str:
        msg=msg.decode()
    msg=msg.replace("'",'"')
    try:
        #See if the json itself has a problem
        json_msg=json.loads(msg)
        print(json_msg)
    except Exception as e:
        print()
        logger.error(f"Block received is not valid JSON !: {e}")