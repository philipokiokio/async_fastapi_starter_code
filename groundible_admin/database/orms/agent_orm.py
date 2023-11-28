from sqlalchemy.dialects.postgresql import UUID
from . import AbstractBase

from sqlalchemy import String, Column, Date, DateTime
from uuid import uuid4


class AgentRecord(AbstractBase):
    __tablename__ = "agent_record"
    agent_uid = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    admin_uid = Column(UUID(as_uuid=True), index=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    email = Column(String, nullable=False, unique=True)
    phone_number = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    last_survey_update = Column(DateTime, nullable=True)
