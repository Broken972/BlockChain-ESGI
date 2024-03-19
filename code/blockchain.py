# Importation des modules nécessaires
import hashlib
import json
import sys
from functions import *
from flask import Flask, request, jsonify, Response
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import os
import time
# Messages de réponse pour l'authentification
auth_failed = {"status": "error", "message": "Authentication failed"}
auth_succeed = {"status": "success", "message": "Authenticated successfully"}

# Indicateur si le nœud actuel est un nœud de démarrage (bootstrap)
is_bootstrap_node = True

# Informations globales sur les clés publiques et la chaîne de blocs
global public_keys, chain

# Initialisation de l'application Flask
app = Flask(__name__)

def authenticate_user():
    data = request.json
    if authenticate(data, public_keys):
        return auth_succeed
    else:
        return auth_failed

# Classe pour représenter un bloc dans la blockchain GeekCoin
class CoinBlock:

    def __init__(self, previous_block_hash, transaction_list):
        self.previous_block_hash = previous_block_hash
        self.transaction_list = transaction_list
        self.block_data = f"{' - '.join(transaction_list)} - {previous_block_hash}"
        self.block_hash = hashlib.sha256(self.block_data.encode()).hexdigest()


# Classe pour gérer la blockchain
class Blockchain:
    def __init__(self):
        self.chain = []
        self.generate_genesis_block()

    def generate_genesis_block(self):
        self.chain.append(CoinBlock("0", ['Genesis Block']))

    def create_block_from_transaction(self, transaction_list):
        previous_block_hash = self.last_block.block_hash
        self.chain.append(CoinBlock(previous_block_hash, transaction_list))

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

# Route Flask pour obtenir la liste des blocs de la blockchain
@app.route('/blockchain_list', methods=['GET'])
def blockchain_data():
    data=request
    if authenticate(data, public_keys):
        return jsonify(chain)
    else:
        return auth_failed

# Route Flask pour obtenir santé du node
@app.route('/health', methods=['GET'])
def blockchain():
    try:
        chain = load_blockchain_data()
        public_keys = load_verified_public_keys()
        # Use jsonify to automatically convert the dictionary to a JSON response
        return jsonify({'Status': 'Working as expected'}), 200
    except Exception as error:
        print("[!] Impossible de récuperer les données nécessaire")
        # Similarly, use jsonify for the error response
        return jsonify({'Status': 'Error'}), 500
    

# Route Flask pour obtenir la liste des clés publiques
@app.route('/keys_list', methods=['GET'])
def keys_data():
    data=request
    if authenticate(data, public_keys):
        return public_keys
    else:
        return auth_failed


# Point d'entrée principal pour l'exécution de l'application
if __name__ == "__main__":
    myblockchain = Blockchain()
    while True:
        time.sleep(10)
        try:
            load_blockchain_data()
        except:
            try:
                chain = retrieve_blockchain()
            except:
                print("[*] Error retrieving blockchain")
        try:
            public_keys = load_verified_public_keys()
        except:
            try:
                public_key = retrieve_public_keys()
            except:
                print("[*] Error retrieving public keys")
        break
    print("[*] Noeud lancé")
    app.run(debug=True,host="0.0.0.0",port=os.environ.get('LISTEN_PORT'))
