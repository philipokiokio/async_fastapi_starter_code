import logging
from typing import Optional
from groundible_admin.schemas.auth_schemas import (
    AdminUser,
    AdminUserExtended,
    AdminUserUpdate,
    NewAgentProfile,
    UserAccessToken,
)
import groundible_admin.database.db_handlers.auth_db_handler as admin_user_db_handler
from uuid import UUID, uuid4
from fastapi import HTTPException
from groundible_admin.services.service_utils.exception_collection import (
    CreateError,
    DuplicateError,
    NotFound,
    UpdateError,
)
import groundible_admin.services.service_utils.gr_redis_utils as redis_utils
import groundible_admin.services.service_error_enums as service_errors
import groundible_admin.services.service_utils.auth_utils as auth_utils
import json
import groundible_admin.services.service_utils.token_utils as gr_toks_utils
from groundible_admin.root.utils.mailer import send_mail

LOGGER = logging.getLogger(__name__)


async def get_admin_user_by_mail(email: str):
    try:
        return await admin_user_db_handler.get_admin(email=email)
    except NotFound as e:
        LOGGER.exception(e)
        LOGGER.error("Admin not found")
        raise HTTPException(**service_errors.ErrorEnum.agent_not_found())


async def get_admin_user(agent_uid: UUID):
    try:
        return await admin_user_db_handler.get_admin_profile(agent_uid=agent_uid)
    except NotFound as e:
        LOGGER.exception(e)
        LOGGER.error("Agent not found")

        raise HTTPException(**service_errors.ErrorEnum.agent_not_found())


# create record
async def admin_sign_up(admin_user: AdminUser):
    """Create Admin Token

    Args:
        invite_token (AgentInviteToken): _description_

    Raises:
        HTTPException: invalid_token

    Returns:
        _type_: _description_
    """
    try:
        admin_profile = await get_admin_user_by_mail(email=admin_user.email)

        if admin_profile:
            LOGGER.error("Admin Account: exists")

            raise HTTPException(**service_errors.ErrorEnum.email_exists())
    # else create record
    except HTTPException:
        admin_user.password = auth_utils.hash_password(
            plain_password=admin_user.password
        )

        admin_profile = await admin_user_db_handler.create_admin(
            admin_user=AdminUserExtended(**admin_user.model_dump())
        )
        admin_profile_dict = {"admin_uid": str(admin_profile.admin_uid)}
        access_token, refresh_token = (
            auth_utils.create_access_token(data=admin_profile_dict),
            auth_utils.create_refresh_token(data=admin_profile_dict),
        )

        return UserAccessToken(access_token=access_token, refresh_token=refresh_token)


# login
async def admin_login(email: str, password: str):
    admin_profile = await get_admin_user_by_mail(email=email)
    if not auth_utils.verify_password(
        hashed_password=admin_profile.password, plain_password=password
    ):
        raise HTTPException(**service_errors.ErrorEnum.incorrect_credential())

    payload = NewAgentProfile(agent_uid=admin_profile.admin_uid, email=email)

    payload_dict = {"admin_uid": str(payload.agent_uid), "email": payload.email}
    access_token, refresh_token = auth_utils.create_access_token(
        data=payload_dict
    ), auth_utils.create_refresh_token(data=payload_dict)

    return UserAccessToken(access_token=access_token, refresh_token=refresh_token)


# forget password
async def forgot_password(email: str):
    await get_admin_user_by_mail(email=email)

    # Create a Token 4 OTP
    token = gr_toks_utils.gr_token_gen()

    redis_utils.add_forget_admin_token(token=token, email=email)
    # send mail

    await send_mail(
        subject="Forgot Password",
        reciepients=[email],
        payload={"token": token},
        template="user_auth/token_email_template.html",
    )
    return {"messge": "mail sent"}

    ...


async def admin_update(admin_update: AdminUserUpdate, admin_user_uid: UUID):
    try:
        return await admin_user_db_handler.update_agent(
            admin_user_update=admin_update, admin_user_uid=admin_user_uid
        )
    except UpdateError as e:
        LOGGER.exception(e)
        LOGGER.error("unexplainable update error")
        raise HTTPException(**service_errors.ErrorEnum.agent_not_found())


async def reset_password(token: int, new_password: str):
    email = redis_utils.get_forget_admin_token(token=token)
    if not email:
        LOGGER.error(f"forgot password token: {token} not valid")
        raise HTTPException(**service_errors.ErrorEnum.redis_not_found())

    admin_profile = await get_admin_user_by_mail(email=email)

    new_password = auth_utils.hash_password(plain_password=new_password)
    updated_admin_profile = await admin_update(
        admin_update=AdminUserUpdate(password=new_password),
        admin_user_uid=admin_profile.admin_uid,
    )
    return updated_admin_profile


async def admin_logout(access_token: str, refresh_token: str):
    redis_utils.add_token_blacklist(
        access_token=access_token, refresh_token=refresh_token
    )

    return {}
