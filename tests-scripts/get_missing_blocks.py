import json

def load_blockchain_from_file(file_path):
    """
    Loads the blockchain from a file.
    """
    with open(file_path, 'r') as file:
        blockchain = json.load(file)
    return blockchain

def get_block(blockchain, block_hash):
    """
    Retrieves a block from the blockchain.
    """
    for block in blockchain:
        if block['block_hash'] == block_hash:
            return block
    return None

def get_subsequent_blocks(blockchain, block_hash):
    """
    Retrieves all blocks following the given block_hash.
    """
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

# Example Usage
blockchain = load_blockchain_from_file('../code/blockchain_data.json')

# Retrieve all blocks following a specific block_hash
block_hash = "092e63921486f303054371188aa2ff2e3ea77cfbbe016db0addcd19470b45573"
subsequent_blocks = get_subsequent_blocks(blockchain, block_hash)
for block in subsequent_blocks:
    print(block)
