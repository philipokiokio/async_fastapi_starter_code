from groundible_client.root.app import settings
from groundible_client.root.app import app
from pytest_postgresql import factories
from uuid import uuid4
from fakeredis.aioredis import FakeRedis
from fastapi.testclient import TestClient
import pytest


@pytest.fixture(scope="session")
async def mock_redis():
    fake_redis = FakeRedis(decode_responses=True)
    yield fake_redis
    # Clean up the FakeRedis instance after the test
    fake_redis.connection_pool.disconnect()


@pytest.fixture(scope="session")
async def mock_postgres():
    postgresql = factories.postgresql(process_fixture_name=str(uuid4()))
    yield postgresql


@pytest.fixture(scope="session")
async def app_test_client_fixture(mock_postgres, mock_redis):
    redis_url = mock_redis.url
    postgres_url = mock_postgres.dsn()

    settings.postgres_url = postgres_url
    settings.redis_url = redis_url

    with TestClient(app=app) as test_client:
        yield test_client
