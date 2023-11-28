from groundible_admin.root.database import DeclarativeBase
from sqlalchemy import Column, DateTime

from datetime import datetime


class AbstractBase(DeclarativeBase):
    __abstract__ = True
    date_created_utc = Column(DateTime(), default=datetime.utcnow)
    date_updated_utc = Column(DateTime(), onupdate=datetime.utcnow)

    def as_dict(self):
        return {field.name: getattr(self, field.name) for field in self.__table__.c}
