from fastapi import FastAPI, Depends,Request
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
import sys
import base64,hashlib
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
sys.path.insert(0, '..')

from functions import *
from functions.tailscale_functions import *
async def jwks_function(request: Request):
    client_ip = request.client.host
    # Load the RSA public key from a file
    with open('./keys/public_key.pem', 'rb') as f:
        public_key = serialization.load_pem_public_key(f.read(), backend=default_backend())
    public_numbers = public_key.public_numbers()
    modulus = base64.urlsafe_b64encode(public_numbers.n.to_bytes((public_numbers.n.bit_length() + 7) // 8, 'big')).decode('utf-8').rstrip('=')
    exponent = base64.urlsafe_b64encode(public_numbers.e.to_bytes((public_numbers.e.bit_length() + 7) // 8, 'big')).decode('utf-8').rstrip('=')
    our_vpn_ip = get_tailscale_ip_address()
    if client_ip != our_vpn_ip:
        return JSONResponse(content={'status': 'Error','msg': f'unauthorized {client_ip}'}, status_code=403)
    key = base64.urlsafe_b64encode(os.environ.get('JWT_SECRET_KEY').encode()).decode().rstrip('=')
    # jwk = {
    #     'kty': 'oct',
    #     'k': key,
    #     'alg': 'RS256',
    #     'use': 'sig',
    #     'kid': hashlib.sha256(key.encode()).hexdigest()
    # }
    jwk = {
        "alg": "RS256",
        "kid": hashlib.sha256(key.encode()).hexdigest(),
        "k": key,
        "kty": "RSA",
        "use": "sig",
        "n": modulus,
        "e": exponent
    }
    jwks = {'keys': [jwk]}
    return JSONResponse(content=jwks, status_code=200)