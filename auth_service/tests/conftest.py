import importlib
import os
from typing import AsyncIterator

import httpx
import pytest


@pytest.fixture()
def app(tmp_path):
    db_path = tmp_path / "auth_test.db"
    os.environ["AUTH_DATABASE_URL"] = f"sqlite+aiosqlite:///{db_path}"
    os.environ["AUTH_SECRET_KEY"] = "test-secret"
    os.environ["AUTH_ALGORITHM"] = "HS256"

    import main as main_module

    importlib.reload(main_module)
    return main_module.app


@pytest.fixture()
async def client(app) -> AsyncIterator[httpx.AsyncClient]:
    # httpx.ASGITransport in некоторых версиях не управляет lifespan,
    # поэтому явно создаём таблицы перед тестами.
    from database import init_db

    await init_db()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

