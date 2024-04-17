# Importation des modules nécessaires
import hashlib
import json
import sys
from functions import *
from flask import Flask, request, jsonify, Response
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from datetime import datetime
from flask_jwt_extended import jwt_required

import os
import time
# Messages de réponse pour l'authentification
auth_failed = {"status": "error", "message": "Authentication failed"}
auth_succeed = {"status": "success", "message": "Authenticated successfully"}

# Indicateur si le node actuel est un node de démarrage (bootstrap)
is_bootstrap_node = True

# Informations globales sur les clés publiques et la chaîne de blocs
global public_keys, chain

# Initialisation de l'application Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret'
jwt = JWTManager(app)
def authenticate_user():
    data = request.json
    if authenticate(data, public_keys):
        return auth_succeed
    else:
        return auth_failed

# # Classe pour représenter un bloc dans la blockchain GeekCoin
# class CoinBlock:

#     def __init__(self, previous_block_hash, transaction_list):
#         self.previous_block_hash = previous_block_hash
#         self.transaction_list = transaction_list
#         self.block_data = f"{' - '.join(transaction_list)} - {previous_block_hash}"
#         self.block_hash = hashlib.sha256(self.block_data.encode()).hexdigest()


# # Classe pour gérer la blockchain
# class Blockchain:
#     def __init__(self):
#         self.chain = []
#         self.generate_genesis_block()

#     def generate_genesis_block(self):
#         self.chain.append(CoinBlock("0", ['Genesis Block']))

#     def create_block_from_transaction(self, transaction_list):
#         previous_block_hash = self.last_block.block_hash
#         self.chain.append(CoinBlock(previous_block_hash, transaction_list))

#     def display_chain(self):
#         for i in range(len(self.chain)):
#             print(f"Data {i + 1}: {self.chain[i].block_data}")
#             print(f"Hash {i + 1}: {self.chain[i].block_hash}\n")

#     def save_to_file(self):
#         chain_data = []
#         for block in self.chain:
#             chain_data.append({
#                 'previous_block_hash': block.previous_block_hash,
#                 'transaction_list': block.transaction_list,
#                 'block_hash': block.block_hash
#             })
#         with open('blockchain_data.json', 'w') as file:
#             json.dump(chain_data, file, indent=4)

#     @property
#     def last_block(self):
#         return self.chain[-1]

# Route Flask pour obtenir la liste des blocs de la blockchain
@app.route('/blockchain_list', methods=['GET'])
@jwt_required()
def blockchain_data():
    data=request
    chain = load_blockchain_data()
    return jsonify(chain)
    # if authenticate(data, public_keys):
    #     return jsonify(chain)
    # else:
    #     return auth_failed

# Route Flask pour obtenir santé du node
@app.route('/health', methods=['GET'])
def blockchain():
    try:
        chain = load_blockchain_data()
        public_keys = load_verified_public_keys()
        return jsonify({'Status': 'Working as expected'}), 200
    except Exception as error:
        print("[!] Impossible de récuperer les données nécessaire")
        return jsonify({'Status': 'Error'}), 500
    

@app.route('/add_block', methods=['POST'])
def add_block():
    request_data = request.get_json()
    try:
       request_data['status']
       request_data['product_name']
       request_data['product_location']
       request_data['product_destination']
       request_data['packages_total_number']
       request_data['packages_total_weight']
       request_data['package_id']
       request_data['product_detail']
    except:
        return jsonify({'Status': 'Error', 'Cause': 'A mendatory field was not defined'}), 400
    try:
        with open("blockchain_data.json", "r") as file:
            chain = json.load(file)
            last_block_hash = chain[-1]['block_hash']
            random_data = os.urandom(32)
            hash_object = hashlib.sha256(random_data)
            random_hash_hex = hash_object.hexdigest()
            current_datetime = datetime.now()
            current_datetime
            new_data = {
                "block_hash": random_hash_hex,
                "previous_block_hash": last_block_hash,
                #"owner":request_data['owner'], WIP
                "time": current_datetime.strftime("%Y-%m-%d|%H:%M:%S"),
                "status": request_data['status'],
                "produit": request_data['product_name'],
                "current_place": request_data['product_location'],
                "destination": request_data['product_destination'],
                "packages_total_number": request_data['packages_total_number'],
                "packages_total_weight": request_data['packages_total_weight'],
                "package_id": request_data['package_id'],
                "product_detail": request_data['product_detail']
            }
            chain.append(new_data)
        with open("blockchain_data.json", "w") as file:
            json.dump(chain, file, indent=4)
        return jsonify({'Status': 'Success'}), 200
    except:
        return jsonify({'Status': 'Error'}), 500


# Route Flask pour obtenir la liste des clés publiques
@app.route('/keys_list', methods=['GET'])
def keys_data():
    data=request
    if authenticate(data, public_keys):
        return public_keys
    else:
        return auth_failed

@app.route('/auth_api', methods=['POST'])
def auth_api():
    data = request.form
    client_public_key = request.form.get('public_key')
    client_signature = request.form.get('signature')
    if client_public_key is None:
        return jsonify({'Error': 'No public key provided'}), 400
    if client_signature is None:
        return jsonify({'Error': 'No signature provided'}), 400
    token = authenticate_api(client_public_key, client_signature, public_keys,app)
    if token != False:
        return jsonify({'Token:': f'{token}'}), 200
    else:
        return "Error while creating token"

# Point d'entrée principal pour l'exécution de l'application
if __name__ == "__main__":
    #myblockchain = Blockchain()
    while True:
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
