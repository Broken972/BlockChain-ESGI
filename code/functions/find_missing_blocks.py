import json
from functions.blockchain_functions import *
from functions.consul.find_available_services import *
from functions.tailscale_functions import *
import random
async def find_missing_blocks():
    blockchain=load_blockchain_data()
    latest_hash=find_latest_block(blockchain)
    print(latest_hash)
    our_node = return_current_tailscale_domains()[0]
    healthy_nodes = await get_healthy_services('blockchain-server',our_node)
    print(healthy_nodes)
    exclude = {our_node}
    filtered_choices = [item for item in healthy_nodes if item not in exclude]
    random_validator = random.choice(filtered_choices)
    health_url = f'https://{random_validator}:5000/health'
    response = requests.get(health_url)
    srv_answer = response.json()
    remote_merkle_root_hash = srv_answer['merkle_root']
    print(remote_merkle_root_hash)
    our_merkle_root = await asyncio.to_thread(calculate_merkle_root_from_json, blockchain)
    if remote_merkle_root_hash != our_merkle_root:
        jwt = obtain_jwt_from_remote(f"{random_validator}:5000")
        print(jwt)
        if "error" not in jwt:
            url = f'https://{random_validator}:5000/send-missing-blocks'
            headers = {
                'Content-Type': "application/x-www-form-urlencoded",
                'Authorization': f'Bearer {jwt}'
            }
            data = {
                'latest_hash': latest_hash
            }
            response = requests.post(url, headers=headers, data=data)
            print(response.status_code)
            if "up to date" not in response.text:
                try:
                    missing_blocks = [response.text]
                    for missing_block in missing_blocks:
                        missing_block=json.loads(missing_block)
                        print("hello")
                        if len(missing_block) == 1:
                            data = missing_block[0]
                            blockchain.append(data)
                        else:
                            for block in missing_block:
                                print(block)
                                blockchain.append(block)
                        with open('blockchain_data.json', 'w') as file:
                            json.dump(blockchain, file, indent=4)
                except Exception as e:
                    print(e)

def get_block(blockchain, block_hash):
    for block in blockchain:
        if block['block_hash'] == block_hash:
            return block
    return None

def find_latest_block(blockchain):
    block_hashes = set(block['block_hash'] for block in blockchain)
    previous_hashes = set(block['previous_block_hash'] for block in blockchain if block['previous_block_hash'])
    latest_block_hashes = block_hashes - previous_hashes

    # There should be only one latest block hash in a valid blockchain
    if len(latest_block_hashes) != 1:
        raise ValueError("Invalid blockchain: there should be exactly one latest block hash")

    latest_block_hash = latest_block_hashes.pop()
    return latest_block_hash

def get_subsequent_blocks(blockchain, block_hash):
    subsequent_blocks = []
    current_block = get_block(blockchain, block_hash)

    if not current_block:
        return subsequent_blocks

    while current_block:
        next_block = None
        for block in blockchain:
            if block['previous_block_hash'] == current_block['block_hash']:
                next_block = block
                subsequent_blocks.append(next_block)
                break
        current_block = next_block

    return subsequent_blocks
