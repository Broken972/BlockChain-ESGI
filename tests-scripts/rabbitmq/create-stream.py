from faststream import FastStream
import asyncio
from faststream.rabbit import RabbitBroker, RabbitExchange, ExchangeType

broker = RabbitBroker(url="amqp://user:password@localhost/")
faststream_app = FastStream(broker)

exch = RabbitExchange("global_exchange", type=ExchangeType.FANOUT)

@faststream_app.on_event("startup")
async def startup_event():
    await broker.publish("Hi!", exchange=exch)

if __name__ == "__main__":
    asyncio.run(faststream_app.run())
