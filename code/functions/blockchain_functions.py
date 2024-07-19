# Importation des modules nécessaires
import hashlib
import json
import sys
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import padding
from fastapi import FastAPI, Depends
from fastapi_jwt_auth import AuthJWT
import base64
import requests
import os
import traceback
import websockets
from datetime import datetime
import asyncio
import pika
import uuid
import psutil
import socket
with open("node_id") as file:
    node_id = file.read()

boostrap_node = [os.environ.get('BOOSTRAPE_NODE')]


def obtain_jwt_from_remote(remote_host):
    try:
        # Load the public key
        with open("./keys/public_key.pem", "rb") as f:
            public_key_pem = f.read()
            public_key = serialization.load_pem_public_key(public_key_pem)

        # Load the private key
        with open("./keys/private_key.pem", "rb") as f:
            private_key_pem = f.read()
            private_key = serialization.load_pem_private_key(private_key_pem, password=None)
    except Exception as e:
        print("[*] Une erreur est survenue lors de la lecture du fichier private_key ou public_key")
        print(e)
        exit()
    message = "EsgiBlockChain".encode('utf-8')
    signature = private_key.sign(
        message,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    signature = base64.b64encode(signature).decode()
    public_key_pem = public_key_pem.decode().replace("\n","")
    url = f'https://{remote_host}/auth_api'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'public_key': public_key_pem,
        'signature': signature
    }
    response = requests.post(url, headers=headers, data=data)
    try:
        token = response.json()["Token:"]
        return token
    except Exception as e:
        return (f"error : {e}")


def load_local_keys():
    try:
        with open("./keys/public_key.pem", "rb") as f:
            public_key_pem = f.read()
            public_key = serialization.load_pem_public_key(public_key_pem)
        # Load the private key
        with open("./keys/private_key.pem", "rb") as f:
            private_key_pem = f.read()
            private_key = serialization.load_pem_private_key(private_key_pem, password=None)
        return public_key_pem,private_key
    except Exception as error:
        print(error)
        print("[*] Une erreur est survenue lors de la lecture du fichier private_key ou public_key")
        exit()

def generate_signature():
    public_key_pem,private_key=load_local_keys()
    message = "valid_block".encode('utf-8')
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    b64singnature = base64.b64encode(signature)
    return b64singnature

def init_headers(public_key,private_key):
    message = "authentication_request".encode('utf-8')
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    public_key_base64 = base64.b64encode(public_key)

    headers={
        "User-Agent":"ESGI-Blockchain-Agent",
        "Identity": os.environ.get('TAILSCALE_HOSTNAME'),
        "PublicKey": public_key_base64.decode(),
        "Signature": signature.hex(),
    }
    return headers

def retrieve_public_keys():
    keys = load_local_keys()
    headers = init_headers(keys[0],keys[1])
    for host in boostrap_nodes:
        # Send request to the server
        response = requests.get(f'http://{host}/keys_list', headers=headers)
        if "error" in response:
            print("[!] Le noeud n'est pas autorisé à rejoindre le réseau")
            exit()
        else:
            with open("verified_public_keys.json", "a") as verified_keys_file:
                verified_keys_file.write(response.text)
            return response.text
    print("[*] Aucun noeud n'a pus être atteint, arrêt de ce noeud.")
    exit()

def retrieve_blockchain(bootstrap_nodes):
    keys = load_local_keys()
    headers = init_headers(keys[0],keys[1])
    for host in boostrap_nodes:
        response = requests.get(f'http://{host}/blockchain_list', headers=headers)
        print(response)
        if "error" in response.text:
            print("[!] Le noeud n'est pas autorisé à rejoindre le réseau")
            exit()
        else:
            with open("blockchain_data.json", "a") as verified_keys_file:
                verified_keys_file.write(response.text)
            return response.text
    print("[*] Aucun noeud n'a pus être atteint, arrêt de ce noeud.")
    exit()

# Fonction pour charger les données de la blockchain depuis un fichier
def load_blockchain_data():
    try:
        with open('blockchain_data.json', 'r') as file:
            json_data = json.load(file)
            print("[*] Données de la blockchain récupérées")
            return json_data
    except:
        print("[!] Impossible de récuperer les données de la blockchain, Tentative de récupération sur le noeud principal....")

# Fonction pour charger les clés publiques vérifiées depuis un fichier
def load_verified_public_keys():
    try:
        with open('verified_public_keys.json', 'r') as file:
            print("[*] Données des clés publiques récupérées")
            return json.load(file)
    except FileNotFoundError:
        print("[!] Impossible de récuperer les données des clés publiques, Tentative de récupération sur le noeud principal....")

def verify_signature(public_key_pem, message, signature):
    try:
        public_key = serialization.load_pem_public_key(public_key_pem.encode())
        public_key.verify(
            signature,
            message,  # message is already bytes
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    
def find_matching_key(data, message, base64_signature):
    signature = base64.b64decode(base64_signature)
    for identity in data['identities']:
        public_key_pem = '\n'.join(identity['public_key'])
        if verify_signature(public_key_pem, message, signature):
            return identity['name']
    return None


# Fonction pour extraire les clés publiques depuis des données JSON
def extract_public_keys(json_data):
    public_keys_info = []

    for identity in json_data['identities']:
        name = identity['name']
        public_key_lines = identity['public_key']
        is_validator = identity['is_validator']
        public_key = '\n'.join(public_key_lines)

        public_keys_info.append({
            'name': name,
            'public_key': public_key,
            'is_validator': is_validator
        })
    return public_keys_info

def write_to_chain(data_to_append):
    blockchain = load_blockchain_data()
    latest_block_hash = blockchain[-1]["block_hash"]
    data_to_append_block_hash = data_to_append["block_hash"]
    if latest_block_hash != data_to_append_block_hash:
        blockchain.append(data_to_append)
        with open("blockchain_data.json", 'w') as file:
            json.dump(blockchain, file, indent=4)

def authenticate_api(client_public_key,signature,approved_public_keys,Authorize):
    print("Client Public Key:", client_public_key)
    decoded_client_signature = base64.b64decode(signature)
    client_public_key = client_public_key.strip("\n")
    for i in approved_public_keys['identities']:
        if i['public_key'] != None:
            current_enumerated_public_key = i['public_key']
            current_enumerated_public_key = " ".join(current_enumerated_public_key)
            current_enumerated_public_key = current_enumerated_public_key.replace(" ","")
            fixed_client_key = client_public_key.replace(" ","")
            print("Key received " + fixed_client_key)
            print("Current local key enumerated " + current_enumerated_public_key)
            if fixed_client_key in current_enumerated_public_key:
                print("found")
                print(i['public_key'])
                public_key_multiline_string = "\n".join(i['public_key'])
                print(public_key_multiline_string)
                serialized_public_key_from_client = serialization.load_pem_public_key(public_key_multiline_string.encode())
                message = "EsgiBlockChain".encode()
                try:
                    serialized_public_key_from_client.verify(
                        (decoded_client_signature),
                        message,
                        padding.PKCS1v15(),
                        hashes.SHA256()
                    )
                    #print("yes")
                    additional_claims = {"aud": "rabbitmq", "roles": "rabbitmq.configure:*/* rabbitmq.read:*/* rabbitmq.write:*/*"}
                    token = Authorize.create_access_token(subject=str(i['name']), user_claims=additional_claims)
                    print("Verification Successful")
                    print("token " + token)
                    return token
                except Exception as e:
                    print("Verification Failed:", e)
                    traceback.print_exc()
                    return False
                break
    return False

def hash_pair(a, b):
    combined = a + b
    return hashlib.sha256(combined.encode('utf-8')).hexdigest()

def calculate_merkle_root(hashes):
    if not hashes:
        return ''
    
    while len(hashes) > 1:
        if len(hashes) % 2 == 1:
            hashes.append(hashes[-1])
        
        new_hashes = []
        for i in range(0, len(hashes), 2):
            new_hashes.append(hash_pair(hashes[i], hashes[i + 1]))
        
        hashes = new_hashes
    
    return hashes[0]

def calculate_merkle_root_from_json(blocks):
    block_hashes = [block['block_hash'] for block in blocks]
    return calculate_merkle_root(block_hashes)