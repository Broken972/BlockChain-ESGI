# faststream_config.py
from faststream import FastStream
from faststream.rabbit import RabbitBroker
broker = RabbitBroker(url="amqp://user:password@localhost/")

faststream_app = FastStream(broker)
