import importlib
import os
from typing import AsyncIterator

import httpx
import pytest


@pytest.fixture()
def app():
    os.environ["GATEWAY_AUTH_URL"] = "http://auth.up"
    os.environ["GATEWAY_IDEAS_URL"] = "http://ideas.up"
    os.environ["GATEWAY_KANBAN_URL"] = "http://kanban.up"
    os.environ["GATEWAY_MATCHING_URL"] = "http://match.up"

    import config as config_module
    import main as main_module

    importlib.reload(config_module)
    importlib.reload(main_module)
    return main_module.app


@pytest.fixture()
async def client(app) -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

