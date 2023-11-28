from pydantic import EmailStr
from groundible_admin.schemas.auth_schemas import AdminUserProfile
from . import APIRouter, status, Body, Depends, get_current_user, UUID
import groundible_admin.services.agent_admin_service as agent_service
from groundible_admin.schemas.agent_schemas import (
    AgentProfile,
    PagninatedAgentProfile,
    AgentUpdate,
    PaginatedQuery,
)

api_router = APIRouter(prefix="/v1/agents", tags=["Agent Management"])


@api_router.post(path="/invite", status_code=status.HTTP_201_CREATED)
async def invite_agent(
    email: EmailStr = Body(embed=True),
    admin_profile: AdminUserProfile = Depends(get_current_user),
):
    return await agent_service.create_admin_agent(
        admin_uid=admin_profile.admin_uid, email=email
    )


@api_router.get(
    path="/{agent_uid}", status_code=status.HTTP_200_OK, response_model=AgentProfile
)
async def get_agent(
    agent_uid: UUID, admin_profile: AdminUserProfile = Depends(get_current_user)
):
    return await agent_service.get_admin_agent(
        agent_uid=agent_uid, admin_uid=admin_profile.admin_uid
    )


@api_router.get(
    path="", status_code=status.HTTP_200_OK, response_model=PagninatedAgentProfile
)
async def get_agents(
    pagniated_query: PaginatedQuery = Depends(PaginatedQuery),
    admin_profile: AdminUserProfile = Depends(get_current_user),
):
    # depends on the Query

    return await agent_service.get_admin_agents(
        admin_uid=admin_profile.admin_uid, **pagniated_query.model_dump()
    )


# DELETE RECORD
@api_router.delete(path="/{agent_uid}", status_code=status.HTTP_200_OK)
async def delete_agent(
    agent_uid: UUID,
    admin_profile: AdminUserProfile = Depends(get_current_user),
):
    return await agent_service.delete_admin_agent(agent_uid=agent_uid)


# UPDATE RECORD
@api_router.patch(
    path="/{agent_uid}", status_code=status.HTTP_200_OK, response_model=AgentProfile
)
async def update_agent(
    agent_uid: UUID,
    agent_update: AgentUpdate,
    admin_profile: AdminUserProfile = Depends(get_current_user),
):
    return await agent_service.update_admin_agent(
        agent_uid=agent_uid, agent_update=agent_update
    )
