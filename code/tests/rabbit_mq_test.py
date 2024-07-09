import pika
import json
import threading
import uuid
import time

# Generate a unique identifier for this node
node_id = str(uuid.uuid4())

# Load the blockchain from a file
def load_blockchain(filename='blockchain_data.json'):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Save the blockchain to a file
def save_blockchain(blockchain, filename='blockchain_data.json'):
    with open(filename, 'w') as file:
        json.dump(blockchain, file, indent=4)

def get_connection_parameters(nodes):
    credentials = pika.PlainCredentials('rabbitmq', 'rabbitmq')
    parameters = [
        pika.ConnectionParameters(
            host=node,
            credentials=credentials,
            connection_attempts=5,
            retry_delay=2,
            heartbeat=600,
            blocked_connection_timeout=300
        )
        for node in nodes
    ]
    return parameters

def publish_update(block, is_resend=False, attempt=1, max_attempts=2):
    # Load the current blockchain if not a resend
    if not is_resend:
        blockchain = load_blockchain()

        # Add the new block to the blockchain
        blockchain.append(block)

        # Save the updated blockchain
        save_blockchain(blockchain)

    # Add the node identifier to the block
    message = {
        "node_id": node_id,
        "block": block,
        "attempt": attempt
    }

    # Define connection parameters with multiple RabbitMQ nodes
    nodes = ['kali.tailc2844.ts.net', 'node-local-kali.tailc2844.ts.net']
    parameters = get_connection_parameters(nodes)

    connection = None
    for param in parameters:
        try:
            connection = pika.BlockingConnection(param)
            break
        except pika.exceptions.AMQPConnectionError:
            print(f"Connection to {param.host} failed. Trying next node...")
    else:
        raise Exception("All RabbitMQ nodes are unreachable")

    channel = connection.channel()
    channel.queue_declare(queue='blockchain_updates', durable=True)
    channel.basic_publish(exchange='', routing_key='blockchain_updates', body=json.dumps(message))
    print(f" [x] Sent block: {block} (resend: {is_resend}, attempt: {attempt})")
    connection.close()

def callback(ch, method, properties, body):
    message = json.loads(body)
    sender_id = message["node_id"]
    block = message["block"]
    attempt = message.get("attempt", 1)

    # If the message is from this node, resend it with a limit on the number of attempts
    if sender_id == node_id:
        if attempt < 2:
            print(f" [x] Resending block from this node: {block} (attempt: {attempt})")
            publish_update(block, is_resend=True, attempt=attempt + 1)
        else:
            print(f" [x] Resend attempt limit reached for block: {block}")
        return

    print(f" [x] Received block: {block}")

    # Load the current blockchain
    blockchain = load_blockchain()

    # Append the block to the blockchain
    blockchain.append(block)

    # Save the updated blockchain
    save_blockchain(blockchain)

def start_subscriber():
    nodes = ['kali.tailc2844.ts.net', 'node-local-kali.tailc2844.ts.net']
    parameters = get_connection_parameters(nodes)

    connection = None
    for param in parameters:
        try:
            connection = pika.BlockingConnection(param)
            break
        except pika.exceptions.AMQPConnectionError:
            print(f"Connection to {param.host} failed. Trying next node...")
    else:
        raise Exception("All RabbitMQ nodes are unreachable")

    channel = connection.channel()
    channel.queue_declare(queue='blockchain_updates', durable=True)
    channel.basic_consume(queue='blockchain_updates', on_message_callback=callback, auto_ack=True)
    print(' [*] Waiting for blockchain updates. To exit press CTRL+C')
    channel.start_consuming()

def start_node():
    # Start subscriber in a separate thread
    subscriber_thread = threading.Thread(target=start_subscriber)
    subscriber_thread.start()

    # Example of publishing new blocks (in a real application, this would be triggered by some event)
    while True:
        new_block_data = input("Enter new block data: ")
        new_block = {
            "index": len(load_blockchain()) + 1,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "data": new_block_data,
            "previous_hash": "0"  # Ideally, you should calculate the hash of the previous block
        }
        try:
            publish_update(new_block)
        except Exception as e:
            print(f"Failed to publish block: {e}")

if __name__ == "__main__":
    start_node()
