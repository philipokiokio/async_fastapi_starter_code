from groundible_admin.schemas.agent_schemas import NewAgent, AgentProfile, AgentUpdate
from uuid import UUID, uuid4
import groundible_admin.database.db_handlers.agent_admin_db_handler as agent_db_handler
import logging
from . import HTTPException
import groundible_admin.services.service_error_enums as service_utils
from groundible_admin.services.service_utils.exception_collection import (
    CreateError,
    DeleteError,
    DuplicateError,
    NotFound,
    UpdateError,
)


LOGGER = logging.getLogger(__file__)


async def create_admin_agent(admin_uid: UUID, email: str):
    agent_uid = uuid4()

    try:
        await get_admin_agent(
            agent_uid=agent_uid, **{"email": email, "admin_uid": admin_uid}
        )
        raise HTTPException(**service_utils.ErrorEnum.agent_found())
    except HTTPException:
        new_agent = NewAgent(agent_uid=agent_uid, email=email)
        try:
            agent_profile = await agent_db_handler.create_agent(
                admin_uid=admin_uid, new_agent=new_agent
            )
            # send to agent

            return agent_profile
        except DuplicateError as e:
            LOGGER.exception(e)
            LOGGER.error("agent duplicate found")
            raise HTTPException(**service_utils.ErrorEnum.agent_found())


async def get_admin_agent(agent_uid: UUID, **kwargs):
    try:
        return await agent_db_handler.get_admin_agent(agent_uid=agent_uid, **kwargs)
    except NotFound as e:
        logging.error(f"There is no agent with agent_uid: {agent_uid}")
        raise HTTPException(**service_utils.ErrorEnum.agent_not_found())


async def get_admin_agents(admin_uid: UUID, **kwargs):
    return await agent_db_handler.get_admin_agents(admin_uid=admin_uid, **kwargs)
    ...


async def update_admin_agent(agent_uid: UUID, agent_update: AgentUpdate):
    try:
        updated_agent_profile = await agent_db_handler.update_agent(
            agent_uid=agent_uid, agent_update=agent_update
        )

        return updated_agent_profile
    except UpdateError as e:
        LOGGER.exception(e)
        LOGGER.error(
            f"update for agent_uid: {agent_uid}, with payload: {agent_update.model_dump()}"
        )
        raise HTTPException(**service_utils.ErrorEnum.agent_not_found())


async def delete_admin_agent(agent_uid: UUID):
    try:
        await get_admin_agent(agent_uid=agent_uid)

        # trigger the job to Client Side
        await agent_db_handler.delete_agent(agent_uid=agent_uid)
        return {}
    except DeleteError as e:
        LOGGER.exception(e)
        LOGGER.error(f"delete for agent_uid: {agent_uid} failed")
        raise HTTPException(**service_utils.ErrorEnum.agent_not_found())


# Listener
