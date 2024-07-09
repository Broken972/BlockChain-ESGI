import pika
import requests
from requests.auth import HTTPBasicAuth
def rabbit_create_remote_connections_parameters(host,username,jwt_token):
    try:
        credentials = pika.PlainCredentials(username, jwt_token)
        connection_params = pika.ConnectionParameters(
            host=host,
            port=5672,
            virtual_host='/',
            credentials=credentials
        )
        return connection_params
    except Exception as e:
        return e

def rabbit_create_local_connections_parameters():
    try:
        credentials = pika.PlainCredentials("user", "password")
        connection_params = pika.ConnectionParameters(
            host="localhost",
            port=5672,
            virtual_host='/',
            credentials=credentials
        )
        return connection_params
    except Exception as e:
        print(e)
        return False

def rabbit_create_own_node_queue(connection_params,tailscale_short_domain):
    try:
        connection = pika.BlockingConnection(connection_params)
        channel = connection.channel()
        channel.queue_declare(queue=tailscale_short_domain, durable=True)
        return True
    except Exception as e:
        print(e)
        return False
    
def rabbit_check_health():
    url = 'http://localhost:15672/api/healthchecks/node'
    auth = HTTPBasicAuth('user', 'password')
    try:
        response = requests.get(url, auth=auth)
    except:
        return ["dead","impossible to reach"]
    if response.status_code == 200:
        data = response.json()
        status = data.get('status')
        return ["ok",status]
    else:
        return ["dead",response.status_code]
        #print(f"Failed to retrieve data: {response.status_code}")