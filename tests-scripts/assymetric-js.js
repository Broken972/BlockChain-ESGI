const crypto = require('crypto');
const fs = require('fs');

// Function to read key from file
function readKeyFile(filePath) {
  return fs.readFileSync(filePath, 'utf8');
}

// Load the RSA key pair from files
const privateKey = readKeyFile('../code/keys/private_key.pem');
const publicKey = readKeyFile('../code/keys/public_key.pem');

const message = 'This is a secret message';

// Sign the message
const signer = crypto.createSign('SHA256');
signer.update(message);
const signature = signer.sign(privateKey, 'base64');

console.log(`Signature: ${signature}`);

// Verify the signature
const verifier = crypto.createVerify('SHA256');
verifier.update(message);
const isVerified = verifier.verify(publicKey, signature, 'base64');

console.log(`Is verified: ${isVerified}`);
