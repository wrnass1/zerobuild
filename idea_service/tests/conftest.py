import importlib
import os
from typing import AsyncIterator

import httpx
import pytest


@pytest.fixture()
def app(tmp_path):
    db_path = tmp_path / "ideas_test.db"
    os.environ["IDEA_DATABASE_URL"] = f"sqlite+aiosqlite:///{db_path}"
    os.environ["IDEA_JWT_SECRET_KEY"] = "test-secret"
    os.environ["IDEA_JWT_ALGORITHM"] = "HS256"

    import main as main_module

    importlib.reload(main_module)
    return main_module.app


@pytest.fixture()
async def client(app) -> AsyncIterator[httpx.AsyncClient]:
    from database import init_db

    await init_db()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture()
def auth_header():
    # Создаём JWT вручную: ideas использует общий секрет с auth.
    from jose import jwt

    token = jwt.encode({"sub": "1"}, "test-secret", algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}

