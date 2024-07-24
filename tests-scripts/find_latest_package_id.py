import json
from datetime import datetime

def get_latest_block_by_package_id(package_id, filename='../code/blockchain_data.json'):
    with open(filename, 'r') as file:
        blockchain = json.load(file)

    latest_block = None
    latest_time = None

    for block in blockchain:
        try:
            if block["package_id"] == package_id:
                block_time = datetime.strptime(block["time"], "%Y-%m-%d|%H:%M:%S.%f")
                if latest_time is None or block_time > latest_time:
                    latest_time = block_time
                    latest_block = block
        except:
            pass

    return latest_block

# Example usage:
package_id_to_find = "9729729713"
latest_block = get_latest_block_by_package_id(package_id_to_find)
if latest_block:
    print("Latest block with package ID {}: {}".format(package_id_to_find, latest_block))
else:
    print("No block found with package ID {}".format(package_id_to_find))
