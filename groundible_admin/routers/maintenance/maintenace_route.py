from fastapi import APIRouter, status, Body
import groundible_admin.services.maintenance_service.auth_maintenance as agent_maintenace_service
import groundible_admin.schemas.auth_schemas as schemas
from groundible_admin.services.service_utils.auth_utils import get_current_user

api_router = APIRouter(prefix="/v1/maintenace", tags=["Maintenance Route"])


@api_router.post(
    "/invite",
    status_code=status.HTTP_200_OK,
)
async def invite_agent(
    email: schemas.EmailStr = Body(embed=True),
):
    return await agent_maintenace_service.invite_agent(email=email)
