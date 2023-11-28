from fastapi.testclient import TestClient
import pytest
from tests.conftest import app


@pytest.mark.asyncio
async def test_server_root(app_test_client_fixture: TestClient):
    client = TestClient(app=app)
    result = app_test_client_fixture.get("/")
    assert result.status_code == 200
