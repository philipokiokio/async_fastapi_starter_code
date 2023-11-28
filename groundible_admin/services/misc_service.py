from groundible_admin.schemas.auth_schemas import AdminUserProfile
import groundible_admin.services.service_utils.uploader_utils as space_utils
import logging
from fastapi import UploadFile
from typing import List
from groundible_admin.schemas.misc_schemas import purpose

LOGGER = logging.getLogger(__name__)


async def file_uploader(
    files: List[UploadFile], purpose: purpose, admin_profile: AdminUserProfile
):
    uploaded_resp = []
    for file in files:
        uploaded_resp.append(
            await space_utils.file_uploader(
                file_name=f"{purpose.value}/{str(admin_profile.admin_uid)}-{file.filename.replace(' ', '_')}",
                data=file,
            )
        )
    return uploaded_resp


async def file_delete(uploaded_file: str):
    file_name = uploaded_file.split("/")[-1]
    await space_utils.destroy_file(file_name=file_name)
    return {}
