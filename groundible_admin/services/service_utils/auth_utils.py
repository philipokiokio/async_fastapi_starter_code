from passlib.context import CryptContext
from groundible_admin.root.settings import Settings
from itsdangerous import URLSafeTimedSerializer, BadTimeSignature, BadSignature
import logging
from jose import ExpiredSignatureError, jwt, JWTError
from datetime import timedelta, datetime
from fastapi import HTTPException, status
from groundible_admin.schemas.auth_schemas import AdminUserProfile, TokenData
import groundible_admin.services.service_utils.gr_redis_utils as redis_utils
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends
import groundible_admin.services.auth_service as admin_service
from uuid import UUID
import groundible_admin.services.service_error_enums as service_error
from typing import Optional


LOGGER = logging.getLogger(__name__)

settings = Settings()

# PASSWORD HASHING AND VALIDATOR
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


# AUTHENTICATION
bearer = HTTPBearer()
SECRET_KEY = settings.jwt_secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 60 * 7
REFRESH_SECRET_KEY = settings.ref_jwt_secret_key
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 60 * 7 * 3


# TOP_LEVEL_SIGNER
ITS_DANGEROUS_TOKEN_KEY = settings.second_signer_key


token_signer = URLSafeTimedSerializer(secret_key=ITS_DANGEROUS_TOKEN_KEY)


def sign_token(jwt_token: str) -> str:
    return token_signer.dumps(obj=jwt_token)


def resolve_token(signed_token: str, max_age: int):
    try:
        return token_signer.loads(s=signed_token, max_age=max_age)
    except (BadTimeSignature, BadSignature) as e:
        LOGGER.exception(e)
        raise Exception


def create_access_token(data: dict):
    expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) + datetime.utcnow()
    data.update({"exp": expire})
    encoded_jwt = jwt.encode(claims=data, key=SECRET_KEY, algorithm=ALGORITHM)
    dangerous_access_token = sign_token(jwt_token=encoded_jwt)

    return dangerous_access_token


def create_refresh_token(data: dict):
    expire = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES) + datetime.utcnow()
    data.update({"exp": expire})
    encoded_jwt = jwt.encode(claims=data, key=REFRESH_SECRET_KEY, algorithm=ALGORITHM)

    # add signed_token
    dangerous_refresh_token = sign_token(jwt_token=encoded_jwt)
    return dangerous_refresh_token


async def verify_access_token(token: str):
    cache_token = redis_utils.get_token_blacklist(token=token)
    if cache_token:
        raise HTTPException(detail="black-listed token", status_code=401)

    try:
        jwt_token = resolve_token(
            signed_token=token, max_age=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    except Exception:
        LOGGER.error("Access_token top level signer decrypt failed")
        raise credentials_exception()

    try:
        payload = jwt.decode(token=jwt_token, key=SECRET_KEY, algorithms=[ALGORITHM])

        id: str = payload.get("admin_uid")
        if id is None:
            LOGGER.error(f"Decrypted JWT has not id in payload. {payload}")
            raise credentials_exception()

        token_data = TokenData(admin_uid=UUID(id))
    except (JWTError, ExpiredSignatureError) as e:
        LOGGER.exception(e)
        LOGGER.error("JWT Decryption Error")
        raise credentials_exception()

    return token_data


async def verify_refresh_token(token: str):
    cache_token = redis_utils.get_token_blacklist(token=token)
    if cache_token:
        raise HTTPException(detail="black-listed token", status_code=401)
    try:
        jwt_token = resolve_token(
            signed_token=token, max_age=REFRESH_TOKEN_EXPIRE_MINUTES
        )

    except Exception:
        LOGGER.error("Access_token top level signer decrypt failed")
        raise credentials_exception()

    try:
        payload = jwt.decode(
            token=jwt_token, key=REFRESH_SECRET_KEY, algorithms=ALGORITHM
        )
        id: str = payload.get("admin_uid")
        if id is None:
            await redis_utils.delete_refresh_token(refresh_token=token)
            raise credentials_exception()

        token_data = TokenData(admin_uid=id)
    except (JWTError, ExpiredSignatureError) as e:
        LOGGER.exception(e)
        redis_utils.delete_refresh_token(refresh_token=token)
        raise credentials_exception()

    return token_data


async def get_new_access_token(token: str):
    token_data = await verify_refresh_token(token=token)
    token_dict = {
        "admin_uid": str(token_data.admin_uid),
    }
    return create_access_token(data=token_dict)


def credentials_exception():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(
    auth_credential: HTTPAuthorizationCredentials = Depends(bearer),
):
    if not auth_credential.credentials:
        credentials_exception()

    token = await verify_access_token(token=auth_credential.credentials)

    user = await admin_service.get_admin_user(agent_uid=token.admin_uid)
    return user
