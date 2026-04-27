import importlib
import os
from typing import AsyncIterator

import httpx
import pytest


@pytest.fixture()
def app(tmp_path):
    db_path = tmp_path / "kanban_test.db"
    os.environ["KANBAN_DATABASE_URL"] = f"sqlite+aiosqlite:///{db_path}"
    os.environ["KANBAN_JWT_SECRET_KEY"] = "test-secret"
    os.environ["KANBAN_JWT_ALGORITHM"] = "HS256"
    os.environ["KANBAN_IDEA_SERVICE_URL"] = "http://ideas.test"

    import main as main_module

    importlib.reload(main_module)
    return main_module.app


@pytest.fixture()
async def client(app, monkeypatch) -> AsyncIterator[httpx.AsyncClient]:
    # init tables
    from database import init_db

    await init_db()

    # Mock Idea Service calls used in boards_router.create_board
    async def _fake_fetch_idea(_idea_id: int):
        return {"id": _idea_id, "owner_id": 1}

    monkeypatch.setattr("routers.boards_router.fetch_idea", _fake_fetch_idea)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture()
def auth_header():
    from jose import jwt

    token = jwt.encode({"sub": "1"}, "test-secret", algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}

