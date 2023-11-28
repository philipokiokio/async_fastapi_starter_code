from groundible_admin.root.utils.base_schemas import AbstractModel
from pydantic import EmailStr, conint
from typing import Optional, List, Union


class PaginatedQuery(AbstractModel):
    limit: conint(ge=0) = 10
    offset: conint(ge=0) = 0
