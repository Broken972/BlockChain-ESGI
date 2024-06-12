import asyncio
import sys
import json
from datetime import datetime
import websockets
from find_other_nodes import find_other_nodes
import aiofiles

async def is_blockchain_uptodate(block_hash):
    all_nodes = await find_other_nodes()
    if len(all_nodes) == 0:
        print("[CRITICAL] No nodes are available.")
        sys.exit()
    # Asynchronously read blockchain data from a JSON file.
    async with aiofiles.open("blockchain_data.json", 'r') as file_obj:
        current_blockchain_data = await file_obj.read()
    try:
        data = json.loads(current_blockchain_data)
    except json.JSONDecodeError as e:
        print("[ERROR] Failed to decode JSON:", str(e))
        sys.exit()
    for block in data:
        try:
            if block["block_hash"] == block_hash:
                block = block
        except Exception as e:
            pass
    for node in all_nodes:
        print(f"[*] Checking node data at: {node}")
        try:
            uri = f"ws://{node}:5000/blockchain_update"
            async with websockets.connect(uri) as websocket:
                message = json.dumps(block)
                await websocket.send(message)
                response = await websocket.recv()
                if response == "Transaction Closed.":
                    #Connexion cloturé nous pouvons quitter la function
                    return True
                else:
                    #Dans ce cas le noeud distant manque un ou plusieur hash, nous allons donc lire notre blockchain et renvoyer la liste de tout nos hashs pour éviter de renvoyer toute la blockchain
                    with open("blockchain_data.json", 'r') as file_obj:
                        current_blockchain_data = file_obj.read()
                    try:
                        current_blockchain_data = json.loads(current_blockchain_data)
                    except json.JSONDecodeError as e:
                        print("[CRITICAL] Failed to decode JSON:", str(e))
                        sys.exit()
                    block_hashes_string = '|'.join(block['block_hash'] for block in current_blockchain_data)
                    await websocket.send(block_hashes_string)
                    response = await websocket.recv()
                    if response == "Transaction Closed.":
                        #Connexion cloturé cela veut dire que le noeud distant possèdent tout les mêmes hash que nous. Nous pouvons donc quitter la function
                        return True
                    else:
                        #Ici le noeud distant ne possède pas les mêmes hashs que nous. Nous allons donc récuper les hashs manquants et envoyés les blocks associés à ces hashs
                        all_remote_missing_hashes = response.split('|')
                        list_of_blocks_to_send = {}
                        list_of_blocks_to_send['blocks'] = []
                        for current_remote_missing_hash in all_remote_missing_hashes:
                            block = next((block for block in current_blockchain_data if block['block_hash'] == current_remote_missing_hash), None)
                            if block:
                                list_of_blocks_to_send['blocks'].append(block)

                        list_of_blocks_to_send_json = json.dumps(list_of_blocks_to_send, indent=4)
                        await websocket.send(list_of_blocks_to_send_json)
        except Exception as e:
            print(f"[!] Failed reaching {node} : {e}")
# Run the async function using asyncio.run
if __name__ == "__main__":
    asyncio.run(is_blockchain_uptodate("f4c1d0045fd2d84c6efdcf897746586bbce70b17285973769e64ea5d93cbaf35"))
