from sqlalchemy import Integer, String, Column, Date, ARRAY
from . import AbstractBase
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4


class Admin(AbstractBase):
    __tablename__ = "admin"
    admin_uid = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone_number = Column(String, nullable=True, unique=True)
    password = Column(String, nullable=False)
    company = Column(String, nullable=True)
    job_role = Column(String, nullable=True)
    user_type = Column(String, nullable=False)
