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
