# Importation des modules nécessaires
import hashlib
import json
import sys
from flask import Flask, request, jsonify
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
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

# Fonction pour extraire les clés publiques depuis des données JSON
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

def write_to_chain(data_to_append):
    blockchain = load_blockchain_data()
    latest_block_hash = blockchain[-1]["block_hash"]
    data_to_append_block_hash = data_to_append["block_hash"]
    if latest_block_hash != data_to_append_block_hash:
        blockchain.append(data_to_append)
        with open("blockchain_data.json", 'w') as file:
            json.dump(blockchain, file, indent=4)

def authenticate_api(client_public_key,signature,approved_public_keys):
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
                    token = create_access_token(identity=str(i['name']), additional_claims={"aud": "rabbitmq","roles": "rabbitmq.configure:*/test_queue rabbitmq.read:*/test_queue rabbitmq.write:*/test_queue"})
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

# def get_connection_parameters(nodes):
#     credentials = pika.PlainCredentials('rabbitmq', 'rabbitmq')
#     parameters = [
#         pika.ConnectionParameters(
#             host=node,
#             credentials=credentials,
#             connection_attempts=5,
#             retry_delay=2,
#             heartbeat=600,
#             blocked_connection_timeout=300
#         )
#         for node in nodes
#     ]
#     return parameters

# def callback(ch, method, properties, body):
#     message = json.loads(body)
#     sender_id = message["node_id"]
#     block = message["block"]
#     attempt = message.get("attempt", 1)

#     # If the message is from this node, resend it with a limit on the number of attempts
#     if sender_id == node_id:
#         if attempt < 2:
#             print(f" [x] Resending block from this node: {block} (attempt: {attempt})")
#             publish_update(block, is_resend=True, attempt=attempt + 1)
#         else:
#             print(f" [x] Resend attempt limit reached for block: {block}")
#         return

#     print(f" [x] Received block: {block}")

#     # Save the updated blockchain
#     write_to_chain(block)


# def start_subscriber():
#     nodes = ['node-local-kali-2.tailc2844.ts.net', 'node-local-kali.tailc2844.ts.net']
#     parameters = get_connection_parameters(nodes)

#     connection = None
#     for param in parameters:
#         try:
#             connection = pika.BlockingConnection(param)
#             break
#         except pika.exceptions.AMQPConnectionError:
#             print(f"Connection to {param.host} failed. Trying next node...")
#     else:
#         raise Exception("All RabbitMQ nodes are unreachable")

#     channel = connection.channel()
#     channel.queue_declare(queue='blockchain_updates', durable=True)
#     channel.basic_consume(queue='blockchain_updates', on_message_callback=callback, auto_ack=True)
#     print(' [*] Waiting for blockchain updates. To exit press CTRL+C')
#     channel.start_consuming()


# def publish_update(block, is_resend=False, attempt=1, max_attempts=2):
#     # Load the current blockchain if not a resend
#     if not is_resend:
#         write_to_chain(block)

#     # Add the node identifier to the block
#     message = {
#         "node_id": node_id,
#         "block": block,
#         "attempt": attempt
#     }

#     # Define connection parameters with multiple RabbitMQ nodes
#     nodes = ['node-local-kali-2.tailc2844.ts.net', 'node-local-kali.tailc2844.ts.net']
#     parameters = get_connection_parameters(nodes)

#     connection = None
#     for param in parameters:
#         try:
#             connection = pika.BlockingConnection(param)
#             break
#         except pika.exceptions.AMQPConnectionError:
#             print(f"Connection to {param.host} failed. Trying next node...")
#     else:
#         raise Exception("All RabbitMQ nodes are unreachable")

#     channel = connection.channel()
#     channel.queue_declare(queue='blockchain_updates', durable=True)
#     channel.basic_publish(exchange='', routing_key='blockchain_updates', body=json.dumps(message))
#     print(f" [x] Sent block: {block} (resend: {is_resend}, attempt: {attempt})")
#     connection.close()