import requests
import json
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import base64
try:
    # Load the public key
    with open("public_key.pem", "rb") as f:
        public_key_pem = f.read()
        public_key = serialization.load_pem_public_key(public_key_pem)

    # Load the private key
    with open("private_key.pem", "rb") as f:
        private_key_pem = f.read()
        private_key = serialization.load_pem_private_key(private_key_pem, password=None)
except:
    print("[*] Une erreur est survenue lors de la lecture du fichier private_key ou public_key")
    exit()

message = "EsgiBlockChain".encode('utf-8')

# Sign the message
signature = private_key.sign(
    message,
    padding.PKCS1v15(),
    hashes.SHA256()
)


public_key_base64 = base64.b64encode(public_key_pem)

headers={
    "User-Agent":"ESGI-Blockchain-Agent",
    "Identity": "Noeud-Principal-1",
    "PublicKey": public_key_base64.decode(),
    "Signature": signature.hex(),
}
#print(headers)


print(base64.b64encode(signature))
# Send request to the server
# response = requests.get('http://192.168.1.147:5000/auth', headers=headers)
# json_resp = response.json()
# print(json_resp)
# if json_resp["status"] == "success":
#     print("[*] Le noeud est authorisé à accèder au réseau")
# else:
#     print("[!] Le noeud n'est pas autorisé à rejoindre le réseau")