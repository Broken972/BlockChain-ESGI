# Importation des modules nécessaires
import hashlib
import json
import sys
from flask import Flask, request, jsonify, Response
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from datetime import datetime
from flask_jwt_extended import jwt_required
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
from flask_sockets import Sockets
import os,threading,uuid,base64
import time

#Import API Routes
from api_routes.health import health_function
from api_routes.is_jwt_valid import is_jwt_valid
from api_routes.add_block import add_block
from api_routes.keys_list import keys_list
from api_routes.blockchain_list import blockchain_list
from api_routes.auth_api import auth_api
from api_routes.jwks import jwks_function

#Import functions
from functions.rabbitmq_functions import *
from functions.tailscale_functions import *
from functions.blockchain_functions import *

# Messages de réponse pour l'authentification
auth_failed = {"status": "error", "message": "Authentication failed"}
auth_succeed = {"status": "success", "message": "Authenticated successfully"}

# Indicateur si le node actuel est un node de démarrage (bootstrap)
is_bootstrap_node = True

# Informations globales sur les clés publiques et la chaîne de blocs
global public_keys, chain
# Initialisation de l'application Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')

#Création des routes
app.add_url_rule('/health', 'health', health_function, methods=['GET'])
app.add_url_rule('/is_jwt_valid', 'is_jwt_valid', is_jwt_valid, methods=['GET'])
app.add_url_rule('/add_block', 'add_block', add_block, methods=['POST'])
app.add_url_rule('/keys_list', 'keys_list', keys_list, methods=['GET'])
app.add_url_rule('/blockchain_list', 'blockchain_list', blockchain_list, methods=['GET'])
app.add_url_rule('/auth_api', 'auth_api', auth_api, methods=['POST'])
app.add_url_rule('/.well-known/jwks.json', 'jwks_function', jwks_function, methods=['GET'])

jwt = JWTManager(app)
sockets = Sockets(app)

# Point d'entrée principal pour l'exécution de l'application
if __name__ == "__main__":
    try:
        our_domain,our_short_domain = return_current_tailscale_domains()
        print(f"[*] Acquired tailscale IP : {our_domain}")
    except:
        print("[ERROR] : Impossible to acquire tailscale IP stopping...")
        sys.exit()
    params = rabbit_create_local_connections_parameters()
    if params == False:
        print("[ERROR] : Impossible to create local connections parameters to rabbitmq stopping here....")
        sys.exit()
    print("[*] Created local parameters")
    own_queue = rabbit_create_own_node_queue(params,our_short_domain)
    if own_queue == False:
        print("[ERROR] : Impossible to create local queue stopping here....")
        sys.exit()
    print("[*] Created local queue")
    while True:
        try:
            load_blockchain_data()
        except Exception as e:
            print(f"[!] Error loading local blockchain : {e}")
            # try:
            #     chain = retrieve_blockchain()
            # except Exception as e:
            #     print(f"[!] Error retrieving blockchain {e}")
        try:
            public_keys = load_verified_public_keys()
        except Exception as e:
            print(f"[!] Error loading local public_keys  : {e}")
            # try:
            #     public_key = retrieve_public_keys()
            # except Exception as e:
            #     print(f"[!] Error retrieving public keys : {e}")
        break
    print("[*] Noeud lancé")
    nodes=asyncio.run(find_other_nodes())
    print(nodes)
    #server = pywsgi.WSGIServer(('0.0.0.0', int(os.environ.get('LISTEN_PORT', 5000))), app, handler_class=CustomWebSocketHandler)
    server = pywsgi.WSGIServer(('0.0.0.0', int(os.environ.get('LISTEN_PORT', 5000))),app,keyfile='node.key', certfile='node.crt')
    server.serve_forever()
