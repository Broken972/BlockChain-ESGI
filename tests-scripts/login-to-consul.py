import consul
import requests

# Replace these variables with your actual values
CONSUL_ADDRESS = 'localhost'
CONSUL_PORT = 8500
#JWT_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcyMDU0NTcwNywianRpIjoiYzU3YzUyZTItZDhjMy00ZjUxLTljYjgtMzlkNGNmZDhiODkxIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6Ik1heCBUZXN0cyIsIm5iZiI6MTcyMDU0NTcwNywiZXhwIjoxNzIwNTQ2NjA3LCJhdWQiOiJyYWJiaXRtcSIsInJvbGVzIjoicmFiYml0bXEuY29uZmlndXJlOiovdGVzdF9xdWV1ZSByYWJiaXRtcS5yZWFkOiovdGVzdF9xdWV1ZSByYWJiaXRtcS53cml0ZToqL3Rlc3RfcXVldWUifQ.Hg7nRq9n4M2q0WdhcHbYcrKMDHMOkWf_sA6QmzdBoRQ'

JWT_TOKEN = input("Enter token : ")

# Function to authenticate using JWT and get a Consul token
def get_consul_token(jwt_token):
    url = f'http://{CONSUL_ADDRESS}:{CONSUL_PORT}/v1/acl/login'
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'AuthMethod': 'jwt',
        'BearerToken': jwt_token
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()['SecretID']

# Authenticate and get a Consul token
consul_token = get_consul_token(JWT_TOKEN)

# Connect to Consul using the obtained token
c = consul.Consul(host=CONSUL_ADDRESS, port=CONSUL_PORT, token=consul_token)

# Test connection by getting the list of nodes
index, nodes = c.catalog.nodes()
print(f'Nodes: {nodes}')

# Test reading a key-value pair (assuming a key 'test' exists)
index, value = c.kv.get('test')
print(f'Test key value: {value}')

# Test setting a key-value pair
c.kv.put('test', 'value')
index, value = c.kv.get('test')
print(f'Updated test key value: {value}')