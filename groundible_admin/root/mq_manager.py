from aio_pika import connect_robust, ExchangeType
from aio_pika.abc import AbstractChannel, AbstractConnection
from groundible_admin.root.settings import Settings
from groundible_admin.schemas.mq_schema import BaseMQMessage
import logging


CHANNEL_MAP = {}
CON_MAP = {}


LOGGER = logging.getLogger(__name__)


QUEUE_NAME = "admin_to_agent"


async def mq_create_connection():
    mq_url = Settings().rabbitmq_url
    connection = await connect_robust(mq_url)

    # async with connection:
    # Declaring queue
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)

    gr_agent_exchange = await channel.declare_exchange(
        "gr_agent",
        ExchangeType.FANOUT,
    )
    queue = await channel.declare_queue(QUEUE_NAME, durable=True)

    await queue.bind(gr_agent_exchange)
    CHANNEL_MAP["channel"] = channel
    CON_MAP["conn"] = connection
    LOGGER.info("connection and channel established")
    return connection


def get_channel():
    channel: AbstractChannel = CHANNEL_MAP.get("channel")
    if not channel:
        raise LookupError("MQ channel does not exist")
    return channel


def get_conn():
    connection: AbstractConnection = CON_MAP.get("conn")

    if not connection:
        raise LookupError("MQ connection does not exist")
    return connection


async def start_consumer(listener: callable):
    connection = get_conn()
    channel = await connection.channel()

    queue = await channel.declare_queue(QUEUE_NAME, durable=True)

    await queue.consume(listener)


async def publish(exchange_name: str, mq_message: BaseMQMessage):
    channel: AbstractChannel = CHANNEL_MAP.get("channel")
    if not channel:
        raise LookupError("MQ connection does not exist")

    exchange = await channel.declare_exchange(name=exchange_name)

    await exchange.publish(
        routing_key=mq_message.routing_action,
        message=mq_message.message.encode(encoding="utf-8"),
    )
