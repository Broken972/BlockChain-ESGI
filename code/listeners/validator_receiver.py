import asyncio
import aio_pika

async def on_message(message: aio_pika.IncomingMessage):
    async with message.process():
        print(f"Received message: {message.body.decode()}")
        with open("test") as file:
            file.write(message.body.decode())

async def validator_receiver_broker():
    # Define the RabbitMQ server URL
    rabbitmq_url = "amqp://user:password@localhost/"
    connection = await aio_pika.connect_robust(rabbitmq_url)
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("validate_block", durable=True)
        await queue.consume(on_message)
        print("[*] En écoute sur le canal de validation...")
    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print("Consumer task cancelled")

def start_rabbitmq_consumer():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(validator_receiver_broker())