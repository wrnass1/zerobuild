import importlib
import os
from typing import AsyncIterator

import httpx
import pytest


@pytest.fixture()
def app():
    os.environ["MATCH_AUTH_URL"] = "http://auth.test"
    os.environ["MATCH_IDEAS_URL"] = "http://ideas.test"
    os.environ["MATCH_JWT_SECRET_KEY"] = "test-secret"
    os.environ["MATCH_JWT_ALGORITHM"] = "HS256"

    # В тестах важно перезагрузить конфиг/зависимости, т.к. Settings читаются при импорте.
    import config as config_module
    import auth_deps as auth_deps_module
    from routers import match_router as match_router_module, invite_router as invite_router_module

    importlib.reload(config_module)
    importlib.reload(auth_deps_module)
    importlib.reload(match_router_module)
    importlib.reload(invite_router_module)

    import main as main_module

    importlib.reload(main_module)
    return main_module.app


@pytest.fixture()
async def client(app) -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture()
def auth_header():
    from jose import jwt

    token = jwt.encode({"sub": "1"}, "test-secret", algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}

