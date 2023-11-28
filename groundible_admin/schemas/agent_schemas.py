from typing import ClassVar
from . import AbstractModel, EmailStr, Optional, List, PaginatedQuery
from uuid import UUID
from pydantic import constr
from datetime import datetime


class NewAgent(AbstractModel):
    agent_uid: UUID
    email: EmailStr


PHONE_NUMBER = constr(max_length=15, min_length=11)


class AgentProfile(NewAgent):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[PHONE_NUMBER] = None
    gender: Optional[str] = None
    last_survey_update: Optional[datetime] = None
    date_created_utc: Optional[datetime] = None


class PagninatedAgentProfile(AbstractModel):
    result_set: List[AgentProfile] = []
    result_size: int = 0


class AgentUpdate(AgentProfile):
    email: ClassVar[EmailStr]
    agent_uid: ClassVar[UUID] = None
    last_survey_update: ClassVar[datetime] = None
    date_created_utc: ClassVar[datetime] = None
