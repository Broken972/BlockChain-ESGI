import pika
import requests
import psutil,socket,requests

def get_tailscale_ip_address():
    adapter_name = "tailscale0"
    addrs = psutil.net_if_addrs()
    if adapter_name in addrs:
        for addr in addrs[adapter_name]:
            if addr.family == socket.AF_INET:
                return addr.address
    return None


def return_current_tailscale_domains():
    api_key = 'tskey-api-kKaTfsavxM11CNTRL-fhfL2skUHYPoTakwwpcvYP2bm8eJpXUmS'
    url = 'https://api.tailscale.com/api/v2/tailnet/parfaite.ppro@gmail.com/devices'
    response = requests.get(url, auth=(api_key, ''))

    if response.status_code == 200:
        devices = response.json()
        my_ip = get_tailscale_ip_address()
        for device in devices['devices']:
            if device['addresses'][0] == my_ip:
                our_domain = device['name']
                dot_position = our_domain.find(".")
                our_short_domain = our_domain[:dot_position]
                return [our_domain,our_short_domain]
    else:
        print(f"Failed to retrieve devices. Status code: {response.status_code}, Error: {response.text}")


def generate_jwt(tailscale_domain):
    jwt_generation_url = f'https://{tailscale_domain}:5000/auth_api'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'public_key': '-----BEGIN PUBLIC KEY-----MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0psIvtzukyDJZuD5l+4BjYYlMQEMXazMywTc6SLVAj31lDnROWBFgMEQwKKBJxfeUhHSYiReJLlhhxzz2XmzbN1WlOqjK2z321GvdIEsjeQZqkEXW5aT4hMU2K4tYGdsYkZNfETpuFCrTKsiGXQ8D6/d/X4gFo9GRjdTUHzfR6fQrcXDMjcQeVT6g7nuz0Xl+VcqGhlRL7WsSCNdHkVPLew32dhOKrZK1Mbh7auGyzZIWuTItabMoY2Igf1J/PxoU5mLfrAdGmzaea1+tEsKwOBI+S+hI+thsBgp5r6vaR1rl6IjoVjg2oIgXbW4THfUezjpLYnkNDyZe9JT8W4BxwIDAQAB-----END PUBLIC KEY-----',
        'signature': 'pBoUNshN8wTgMta6VJOdLyg+xtI3CnidDTW2nkTLmwFnJ3kXI1bLqHUaASJjK54Vrhy9Ex7PbzaDYhYQxeY4aoweWJCVwnuDTa4pVR3qDZJl+j3xWwvhdCxcStPo4TrfcRP73oegG43dOIVjoQMzwSbVcSamVJS/TcgTByHK1R0kAWLIaXzSPk/3/5y5xVNnLo1yDHqMNVXpkxb0YMydiW41pOqfDuVheYEBsPE3T3RC5QQ/n8lrzXGVoaA9OTg/nHwjgMBF5Chmv48NCDbMXerpmUl2R3Fx4kfjblUssQDHMzO2lw2oeHJEX8+xNY73hx92UqFZbddZxm3wO+zf7Q=='
    }
    response = requests.post(jwt_generation_url, headers=headers, data=data)
    if response.status_code != 200:
        raise Exception(f"Failed to get JWT: {response.text}")
    jwt_token = response.json()['Token:']
    return jwt_token

def rabbitmq(jwt_token,our_tailscale_short_domain):
    rabbitmq_host = 'localhost'
    # Setup RabbitMQ connection parameters using JWT
    credentials = pika.PlainCredentials("Max Tests", jwt_token)
    connection_params = pika.ConnectionParameters(
        host=rabbitmq_host,
        port=5672,
        virtual_host='/',
        credentials=credentials
    )

    # Establish connection and open a channel
    try:
        connection = pika.BlockingConnection(connection_params)
        channel = connection.channel()

        # Declare a queue and publish a test message
        queue_name = our_tailscale_short_domain
        channel.queue_declare(queue=queue_name, durable=True)
        channel.basic_publish(exchange='',
                            routing_key=queue_name,
                            body='Hello RabbitMQ!',
                            properties=pika.BasicProperties(
                                delivery_mode=2,  # make message persistent
                            ))
        print("Message sent successfully!")
    except Exception as e:
        print(f"Failed to connect to RabbitMQ: {e}")
    finally:
        if 'connection' in locals() and connection.is_open:
            connection.close()

our_domain,our_short_domain = return_current_tailscale_domains()
jwt_token = generate_jwt(our_domain)
print(jwt_token)
rabbitmq(jwt_token,our_short_domain)
