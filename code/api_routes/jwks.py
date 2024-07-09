from flask import request
import sys
import base64
sys.path.insert(0, '..')

from functions import *

def jwks_function():
    our_vpn_ip = get_tailscale_ip_address()
    if request.remote_addr != our_vpn_ip:
        return jsonify({'status': 'Error', "msg": f"unauthorized {request.remote_addr}"}), 403
    key = base64.urlsafe_b64encode(os.environ.get('JWT_SECRET_KEY').encode()).decode().rstrip('=')
    jwk = {
        'kty': 'oct',
        'k': key,
        'alg': 'HS256',
        'use': 'sig',
        'kid': hashlib.sha256(key.encode()).hexdigest()
    }
    jwks = {'keys': [jwk]}
    return jsonify(jwks)