from groundible_admin.database.orms.auth_orm import Admin as Admin_DB
from . import async_session
import logging
from groundible_admin.schemas.auth_schemas import (
    AdminUserExtended,
    AdminUserProfile,
    AdminUserUpdate,
)
from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError
from groundible_admin.services.service_utils.exception_collection import (
    CreateError,
    DuplicateError,
    NotFound,
    UpdateError,
)
from uuid import UUID

LOGGER = logging.getLogger(__name__)


async def create_admin(admin_user: AdminUserExtended) -> AdminUserProfile:
    async with async_session() as session:
        stmt = insert(Admin_DB).values(admin_user.model_dump()).returning(Admin_DB)
        try:
            result = (await session.execute(statement=stmt)).scalar_one_or_none()
        except IntegrityError as e:
            LOGGER.error(f"duplicate record found for {admin_user.model_dump()}")
            session.rollback()
            raise DuplicateError
        if not result:
            LOGGER.error("create_admin failed")
            session.rollback()
            raise CreateError

        await session.commit()
        return AdminUserProfile(**result.as_dict())


async def get_admin(email: str):
    async with async_session() as session:
        result = (
            await session.execute(select(Admin_DB).where(Admin_DB.email == email))
        ).scalar_one_or_none()

        if not result:
            raise NotFound

        return AdminUserProfile(**result.as_dict())


async def get_admin_profile(agent_uid: UUID):
    async with async_session() as session:
        result = (
            await session.execute(
                select(Admin_DB).where(Admin_DB.admin_uid == agent_uid)
            )
        ).scalar_one_or_none()

        if not result:
            raise NotFound

        return AdminUserProfile(**result.as_dict())


async def update_agent(admin_user_update: AdminUserUpdate, admin_user_uid: UUID):
    async with async_session() as session:
        stmt = (
            update(Admin_DB)
            .where(Admin_DB.admin_uid == admin_user_uid)
            .values(admin_user_update.model_dump(exclude_none=True, exclude_unset=True))
            .returning(Admin_DB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if not result:
            raise UpdateError

        await session.commit()
        return AdminUserProfile(**result.as_dict())


async def delete_user():
    ...
