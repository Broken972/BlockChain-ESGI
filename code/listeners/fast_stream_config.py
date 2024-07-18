# faststream_config.py
from faststream import FastStream
from faststream.rabbit import RabbitBroker,RabbitExchange,ExchangeType,RabbitQueue
from functions.tailscale_functions import *
broker = RabbitBroker(url="amqp://user:password@localhost/")

faststream_app = FastStream(broker)
global_new_block_exch = RabbitExchange("global_new_block_exchange", type=ExchangeType.FANOUT)
our_domain, our_short_domain = return_current_tailscale_domains()
node_queue = RabbitQueue(f"{our_short_domain}_new_block")