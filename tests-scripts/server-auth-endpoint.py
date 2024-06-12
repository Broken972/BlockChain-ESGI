from flask import Flask, request, jsonify
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

app = Flask(__name__)

@app.route('/auth', methods=['GET'])
def authenticate():
    public_key_pem=data.headers.get('public_key')
    signature_encoded=data.headers.get('signature')
    signature=base64.b64decode(signature_encoded)
    signature = bytes.fromhex(data['signature'])
    message = "authentication_request".encode('utf-8')
    public_key = serialization.load_pem_public_key(public_key_pem)
    for i in approved_public_keys['identities']:
        current_public_key = i["public_key"]
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

if __name__ == '__main__':
    app.run(debug=True)
