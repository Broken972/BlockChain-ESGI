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

def retrieve_blockchain():
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

def authenticate_api(client_public_key,signature,approved_public_keys,app):
    print("Client Public Key:", client_public_key)
    decoded_client_signature = base64.b64decode(signature)
    client_public_key = client_public_key.strip("\n")
    for i in approved_public_keys['identities']:
        if i['public_key'] != None:
            current_enumerated_public_key = i['public_key']
            current_enumerated_public_key = " ".join(current_enumerated_public_key)
            current_enumerated_public_key = current_enumerated_public_key.replace(" ","")
            fixed_client_key = client_public_key.replace(" ","")
            if fixed_client_key in current_enumerated_public_key:
                print("found")
                print(i['public_key'])
                public_key_multiline_string = "\n".join(i['public_key'])
                print(public_key_multiline_string)
                serialized_public_key_from_client = serialization.load_pem_public_key(public_key_multiline_string.encode())
                message = "EsgiBlockChain".encode()
                try:
                    serialized_public_key_from_client.verify(
                        decoded_client_signature,
                        message,
                        padding.PKCS1v15(),
                        hashes.SHA256()
                    )
                    print("Verification Successful")
                    token = create_access_token(identity=i['name'])
                    return token
                except Exception as e:
                    print("Verification Failed:", e)
                    traceback.print_exc()
                    return False
                break


# Fonction pour authentifier une demande d'un noeud
def authenticate(data,approved_public_keys):
    public_key_pem_encoded=data.headers.get('Publickey')
    signature=data.headers.get('Signature')
    signature = bytes.fromhex(signature)
    identity=data.headers.get("Identity")
    public_key_pem=base64.b64decode(public_key_pem_encoded)
    message = "authentication_request".encode('utf-8')
    public_key = serialization.load_pem_public_key(public_key_pem)
    for i in approved_public_keys['identities']:
        if identity == i['name']:
            current_public_key = i["public_key"]
            print(signature)
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