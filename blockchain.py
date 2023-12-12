# # For simplicity, let's say each transaction is its own block
# for transaction in json_data['transactions']:
#     transaction_str = f"{transaction['sender']} sends {transaction['amount']} GC to {transaction['receiver']}"
#     myblockchain.create_block_from_transaction([transaction_str])
    #public_keys_info = extract_public_keys(json_data)
# # Printing the extracted information
import hashlib
import json
from flask import Flask, request, jsonify
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

nodes = [
    "192.168.52.1"
]

auth_failed={"status": "error", "message": "Authentication failed"}
auth_succeed={"status": "success", "message": "Authenticated successfully"}

is_bootstrap_node = True

global public_keys,chain

app = Flask(__name__)

def load_blockchain_data():
    try:
        with open('blockchain_data.json', 'r') as file:
            json_data = json.load(file)
            print("[*] Données de la blockchain récupérées")
            return json_data
    except FileNotFoundError:
        print("[!] Impossible de récuperer les données de la blockchain arrêt du noeud....")
        exit()

def load_verified_public_keys():
    try:
        with open('verified_public_keys.json', 'r') as file:
            print("[*] Données des clés publiques récupérées")
            return json.load(file)
    except FileNotFoundError:
        print("[!] Impossible de récuperer les données des clés publiques arrêt du noeud....")
        exit()

class GeekCoinBlock:
    
    def __init__(self, previous_block_hash, transaction_list):
        self.previous_block_hash = previous_block_hash
        self.transaction_list = transaction_list

        self.block_data = f"{' - '.join(transaction_list)} - {previous_block_hash}"
        self.block_hash = hashlib.sha256(self.block_data.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = []
        self.generate_genesis_block()
    
    def generate_genesis_block(self):
        self.chain.append(GeekCoinBlock("0", ['Genesis Block']))
    
    def create_block_from_transaction(self, transaction_list):
        previous_block_hash = self.last_block.block_hash
        self.chain.append(GeekCoinBlock(previous_block_hash, transaction_list))

    def display_chain(self):
        for i in range(len(self.chain)):
            print(f"Data {i + 1}: {self.chain[i].block_data}")
            print(f"Hash {i + 1}: {self.chain[i].block_hash}\n")

    def save_to_file(self):
        chain_data = []
        for block in self.chain:
            chain_data.append({
                'previous_block_hash': block.previous_block_hash,
                'transaction_list': block.transaction_list,
                'block_hash': block.block_hash
            })
        with open('blockchain_data.json', 'w') as file:
            json.dump(chain_data, file, indent=4)

    @property
    def last_block(self):
        return self.chain[-1]


def extract_public_keys(json_data):
    public_keys_info = []
    
    for identity in json_data['identities']:
        name = identity['name']
        public_key_lines = identity['public_key']
        
        public_key = '\n'.join(public_key_lines)
        
        public_keys_info.append({
            'name': name,
            'public_key': public_key
        })
        
    return public_keys_info

def authenticate(data,approved_public_keys):
    public_key_pem = data['public_key'].encode('utf-8')
    signature = bytes.fromhex(data['signature'])
    message = "authentication_request".encode('utf-8')
    public_key = serialization.load_pem_public_key(public_key_pem)
    for i in approved_public_keys['identities']:
        current_public_key = i["public_key"]
        if current_public_key != None:
            current_public_key_encoded = b'\n'.join(map(bytes, [s.encode() for s in current_public_key]))
            current_public_key_encoded += b'\n'
            if current_public_key_encoded == public_key_pem:
                try:
                    # Verify signature
                    public_key.verify(
                        signature,
                        message,
                        padding.PSS(
                            mgf=padding.MGF1(hashes.SHA256()),
                            salt_length=padding.PSS.MAX_LENGTH
                        ),
                        hashes.SHA256()
                    )
                    return True
                except:
                    return False
    return False

@app.route('/blockchain_list', methods=['GET'])
def blockchain_data():
    return chain
    # if authenticated == True:
    #     return chain
    # else:
    #     return auth_failed

@app.route('/keys_list', methods=['GET'])
def keys_data():
    return public_keys

@app.route('/auth', methods=['POST'])
def auth():
    data = request.json
    if authenticate(data,public_keys):
        return auth_succeed
    else:
        return auth_failed

if __name__ == "__main__":
    myblockchain = Blockchain()
    chain = load_blockchain_data()
    public_keys = load_verified_public_keys()
    print("[*] Noeud lancé")
    app.run(debug=True)