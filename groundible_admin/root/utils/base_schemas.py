from pydantic import BaseModel, ConfigDict
from pydantic_settings import BaseSettings


class AbstractSettings(BaseSettings):
    class Config:
        env_file = ".env"
        env_prefix = "gr_admin_"


class AbstractModel(BaseModel):
    model_config = ConfigDict(use_enum_values=True, from_attributes=True)


class AbstractResponse(BaseModel):
    status: int
