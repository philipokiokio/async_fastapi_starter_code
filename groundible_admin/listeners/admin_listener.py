import json
from aio_pika.channel import Channel
from groundible_admin.schemas.mq_schema import BaseMQMessage
from groundible_admin.root.mq_manager import get_channel
import logging

LOGGER = logging.getLogger(__file__)

admin_routing_actions = {
    "agent_created": True,
}


async def admin_listener(channel: Channel, body: str, envelope, properties):
    try:
        data = json.loads(body)
        notice = BaseMQMessage(**data)
        notice.message = json.loads(notice.message)

        if not notice.routing_action:
            raise ValueError("Admin Listener needs routing_action value to proceed")

        if notice.routing_action not in admin_routing_actions:
            raise ValueError(
                f"There is no logic for routing_action: {notice.routing_action}"
            )

        await admin_routing_actions[notice.routing_action](data_obj=notice.message)
        # Acknowledge the message after successful processing
        await envelope.ack()

    except json.JSONDecodeError as json_error:
        LOGGER.error(f"JSON decoding error: {json_error}")
        await envelope.nack(requeue=True)
