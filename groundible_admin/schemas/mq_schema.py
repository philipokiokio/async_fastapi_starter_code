from groundible_admin.schemas import AbstractModel


class BaseMQMessage(AbstractModel):
    message: str
    routing_action: str
