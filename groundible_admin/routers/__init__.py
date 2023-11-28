from fastapi import (
    APIRouter,
    Body,
    status,
    Depends,
    UploadFile,
)
from groundible_admin.services.service_utils.auth_utils import (
    get_current_user,
    AdminUserProfile,
)
from uuid import UUID
