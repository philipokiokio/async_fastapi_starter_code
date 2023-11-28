from sqlalchemy import insert, select, update, delete, and_, or_, func
from sqlalchemy.exc import IntegrityError
from groundible_admin.services.service_utils.exception_collection import (
    CreateError,
    DeleteError,
    DuplicateError,
    NotFound,
    UpdateError,
)
from groundible_admin.schemas.agent_schemas import (
    AgentProfile,
    NewAgent,
    AgentUpdate,
    PagninatedAgentProfile,
)
from uuid import UUID
from . import async_session
import logging
from groundible_admin.database.orms.agent_orm import AgentRecord as AgentRecord_DB

LOGGER = logging.getLogger(__file__)


async def create_agent(admin_uid: UUID, new_agent: NewAgent):
    async with async_session() as session:
        stmt = (
            insert(AgentRecord_DB)
            .values(**new_agent.model_dump(), admin_uid=admin_uid)
            .returning(AgentRecord_DB)
        )
        try:
            result = (await session.execute(statement=stmt)).scalar_one_or_none()

        except IntegrityError:
            LOGGER.exception(IntegrityError)
            LOGGER.error(f"duplicate record found for {new_agent.model_dump()}")
            await session.rollback()
            raise DuplicateError

        if not result:
            LOGGER.error("create_agent failed")
            session.rollback()
            raise CreateError

        await session.commit()
        return AgentProfile(**result.as_dict())


async def get_admin_agent(agent_uid: UUID, **kwargs):
    email = kwargs.get("email")
    admin_uid = kwargs.get("admin_uid")

    or_condition = [AgentRecord_DB.agent_uid == agent_uid]
    and_condition = []

    if email:
        or_condition.append(AgentRecord_DB.email == email)

    if admin_uid:
        print(admin_uid)
        # admin_uid = UUID(admin_uid)
        and_condition.append(AgentRecord_DB.admin_uid == admin_uid)

    async with async_session() as session:
        stmt = select(AgentRecord_DB).where(and_(*and_condition, or_(*or_condition)))

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if not result:
            LOGGER.error(
                f"no record was found for admin_uid: {admin_uid}, and {agent_uid}"
            )

            raise NotFound

        return AgentProfile(**result.as_dict())


async def get_admin_agents(admin_uid: UUID, **kwargs):
    limit = kwargs.get("limit", 10)
    offset = kwargs.get("offset", 0)
    print(limit, offset)
    async with async_session() as session:
        stmt = select(AgentRecord_DB).where(
            and_(
                AgentRecord_DB.admin_uid == admin_uid,
            )
        )
        stmt.offset(offset=offset).limit(limit=limit)
        result = (await session.execute(statement=stmt)).all()
        match_size = (
            await session.execute(
                select(func.count(AgentRecord_DB.admin_uid)).where(
                    AgentRecord_DB.admin_uid == admin_uid
                )
            )
        ).scalar()

        if not result:
            return PagninatedAgentProfile()

        return PagninatedAgentProfile(
            result_set=[AgentProfile(**x[0].as_dict()) for x in result],
            result_size=match_size,
        )


async def update_agent(agent_uid: UUID, agent_update: AgentUpdate):
    update_agent_dict = agent_update.model_dump(exclude_none=True, exclude_unset=True)

    async with async_session() as session:
        stmt = (
            update(AgentRecord_DB)
            .where(agent_uid == agent_uid)
            .values(**update_agent_dict)
            .returning(AgentRecord_DB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if not result:
            await session.rollback()
            raise UpdateError

        await session.commit()
        return AgentProfile(**result.as_dict())


async def delete_agent(agent_uid: UUID):
    async with async_session() as session:
        stmt = (
            delete(AgentRecord_DB)
            .where(agent_uid == agent_uid)
            .returning(AgentRecord_DB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if not result:
            await session.rollback()
            raise DeleteError

        await session.commit()

        return AgentProfile(**result.as_dict())
