from faststream import FastStream
from faststream.rabbit import RabbitBroker,RabbitExchange,ExchangeType,RabbitQueue

global_exchange = RabbitExchange("exchange", type=ExchangeType.FANOUT)

broker = RabbitBroker(url="amqp://user:password@localhost/")
faststream_app = FastStream(broker)

async def declare_smth():
    await broker.connect()
    await broker.declare_exchange(
        RabbitExchange(
            name="global_exchange",
            type=ExchangeType.FANOUT,
        )
    )

    await broker.declare_queue(
        RabbitQueue(
            name="node2_queue",
        )
    )