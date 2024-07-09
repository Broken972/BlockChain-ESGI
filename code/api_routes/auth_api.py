from flask import request, jsonify

import sys
sys.path.insert(0, '..')

from functions.blockchain_functions import authenticate_api
from functions.blockchain_functions import load_verified_public_keys
def auth_api():
    data = request.form
    client_public_key = request.form.get('public_key')
    client_signature = request.form.get('signature')
    if client_public_key is None:
        return jsonify({'Error': 'No public key provided'}), 400
    if client_signature is None:
        return jsonify({'Error': 'No signature provided'}), 400
    token = authenticate_api(client_public_key, client_signature, load_verified_public_keys())
    if token != False:
        return jsonify({'Token:': f'{token}'}), 200
    else:
        return jsonify({'status': 'error', 'msg': 'Unauthorized'})