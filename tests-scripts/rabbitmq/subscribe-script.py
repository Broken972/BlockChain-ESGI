from faststream import FastStream, Logger
from faststream.rabbit import RabbitBroker, RabbitExchange, ExchangeType, RabbitQueue
import asyncio
broker = RabbitBroker(url="amqp://user:password@localhost/")
faststream_app = FastStream(broker)

exch = RabbitExchange("global_exchange", type=ExchangeType.FANOUT)
queue = RabbitQueue("node2_queue")

@broker.subscriber(queue, exch)
async def handle_message(msg, logger: Logger):
    logger.info(f"Received message: {msg}")

if __name__ == "__main__":
    asyncio.run(faststream_app.run())