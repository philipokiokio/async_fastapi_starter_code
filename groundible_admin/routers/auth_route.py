from fastapi import APIRouter, Body, status, Depends
from pydantic import constr

import groundible_admin.services.auth_service as admin_auth_service
import groundible_admin.schemas.auth_schemas as schemas
from groundible_admin.services.service_utils.auth_utils import (
    get_current_user,
    get_new_access_token,
)
from fastapi import Header

api_router = APIRouter(prefix="/v1/auth", tags=["Admin Authentication"])


@api_router.post(
    "/sign-up",
    response_model=schemas.UserAccessToken,
    status_code=status.HTTP_201_CREATED,
)
async def admin_sign_up(admin_user: schemas.AdminUser):
    return await admin_auth_service.admin_sign_up(admin_user=admin_user)


@api_router.post(
    "/login", response_model=schemas.UserAccessToken, status_code=status.HTTP_200_OK
)
async def admin_login(login_cred: schemas.Login):
    return await admin_auth_service.admin_login(
        email=login_cred.email, password=login_cred.password
    )


@api_router.post(
    "/me", response_model=schemas.AdminUserProfile, status_code=status.HTTP_200_OK
)
async def admin_me(
    current_admin_profile: schemas.AdminUserProfile = Depends(get_current_user),
):
    return current_admin_profile


@api_router.get(
    "/refresh-token",
    response_model=schemas.UserAccessToken,
    status_code=status.HTTP_200_OK,
)
async def new_access_token(refresh_token: str = Header(convert_underscores=False)):
    return schemas.UserAccessToken(
        access_token=await get_new_access_token(token=refresh_token),
        refresh_token=refresh_token,
    )


@api_router.post("/logout", status_code=status.HTTP_200_OK)
async def admin_logout(
    token_cred: schemas.UserAccessToken,
    current_admin_user: schemas.AdminUserProfile = Depends(get_current_user),
):
    return await admin_auth_service.admin_logout(
        access_token=token_cred.access_token, refresh_token=token_cred.refresh_token
    )


@api_router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    email: schemas.EmailStr = Body(embed=True, example="agent@gr.com")
):
    return await admin_auth_service.forgot_password(email=email)


@api_router.post(
    "/password-reset",
    status_code=status.HTTP_200_OK,
    response_model=schemas.AdminUserProfile,
)
async def reset_password(
    token: constr(max_length=4, min_length=4) = Body(embed=True, example=1345),
    new_password: str = Body(embed=True),
):
    return await admin_auth_service.reset_password(
        token=token, new_password=new_password
    )
