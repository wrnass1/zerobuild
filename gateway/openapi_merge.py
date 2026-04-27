"""
Сбор и слияние OpenAPI-спецификаций всех сервисов для единого Swagger UI.
"""
from __future__ import annotations

import asyncio
import copy
from typing import Any

import httpx

# (proxy_prefix, merge_path_prefix, schema_prefix) для каждого сервиса.
# merge_path_prefix — префикс в объединённой OpenAPI (чтобы не дублировать путь: у ideas в спеке уже /ideas).
SERVICE_PREFIXES = [
    ("/api/auth", "/api/auth", "Auth_"),
    ("/api/ideas", "/api", "Ideas_"),
    ("/api/kanban", "/api/kanban", "Kanban_"),
    ("/api/match", "/api/match", "Match_"),
]


def _prefix_refs(obj: Any, schema_prefix: str) -> Any:
    """Рекурсивно заменяет $ref на префиксированные имена схем."""
    if isinstance(obj, dict):
        if "$ref" in obj and isinstance(obj["$ref"], str):
            ref = obj["$ref"]
            if ref.startswith("#/components/schemas/"):
                name = ref.split("/")[-1]
                if not name.startswith(("Auth_", "Ideas_", "Kanban_", "Match_")):
                    return {"$ref": f"#/components/schemas/{schema_prefix}{name}"}
            return obj
        return {k: _prefix_refs(v, schema_prefix) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_prefix_refs(item, schema_prefix) for item in obj]
    return obj


def _transform_spec(spec: dict, path_prefix: str, schema_prefix: str) -> tuple[dict, dict]:
    """
    Преобразует спецификацию: префикс путей и переименование схем.
    Возвращает (paths, components).
    """
    paths = {}
    raw_paths = spec.get("paths", {})
    for path_key, path_item in raw_paths.items():
        new_path = path_prefix + (path_key if path_key != "/" else "")
        paths[new_path] = _prefix_refs(copy.deepcopy(path_item), schema_prefix)

    components = spec.get("components", {}) or {}
    schemas = components.get("schemas", {}) or {}
    new_schemas = {}
    for name, schema_obj in schemas.items():
        new_name = schema_prefix + name
        new_schemas[new_name] = _prefix_refs(copy.deepcopy(schema_obj), schema_prefix)
    return paths, new_schemas


async def fetch_openapi(
    client: httpx.AsyncClient,
    base_url: str,
    *,
    retries: int = 5,
    retry_delay: float = 2.0,
) -> dict | None:
    """Загружает openapi.json с сервиса (с повторами при недоступности)."""
    url = f"{base_url.rstrip('/')}/openapi.json"
    for _ in range(retries):
        try:
            resp = await client.get(url, timeout=5.0)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        await asyncio.sleep(retry_delay)
    return None


def _add_security_to_paths(paths: dict) -> None:
    """
    Добавляет security: BearerAuth к эндпоинтам, которые требуют токен.

    Важно: это влияет только на Swagger (какие запросы он отправляет с Authorization),
    а не на фактическую защиту эндпоинтов в сервисах.
    """
    security = [{"BearerAuth": []}]
    # В сервисах `kanban` и `matching` даже read-эндпоинты требуют JWT (Depends(get_current_user_id)),
    # поэтому помечаем их целиком, иначе Swagger не прикрепит Authorization и будет "Not authenticated".
    protected_rules: list[tuple[str, set[str]]] = [
        ("/api/auth/profile", {"get", "put", "post", "delete", "patch"}),
        # Ideas: read публичный, защищаем только операции изменения (create/update/delete)
        ("/api/ideas", {"post", "put", "delete", "patch"}),
        # Kanban: read/write защищены
        ("/api/kanban", {"get", "post", "put", "delete", "patch"}),
        # Matching: read/write защищены
        ("/api/match", {"get", "post", "put", "delete", "patch"}),
    ]

    for path_key, path_item in paths.items():
        for prefix, methods in protected_rules:
            if path_key.startswith(prefix):
                for method in methods:
                    if method in path_item and isinstance(path_item[method], dict):
                        path_item[method]["security"] = security
                break


def _normalize_security_scheme_names(paths: dict) -> None:
    """
    FastAPI по умолчанию называет HTTPBearer-схему как `HTTPBearer`.
    В gateway мы используем единое имя `BearerAuth`, поэтому приводим security-объекты к нему,
    иначе Swagger не сможет сопоставить security requirement с components.securitySchemes.
    """
    for path_item in paths.values():
        if not isinstance(path_item, dict):
            continue
        for op in path_item.values():
            if not isinstance(op, dict):
                continue
            sec = op.get("security")
            if not isinstance(sec, list):
                continue
            new_sec = []
            changed = False
            for req in sec:
                if not isinstance(req, dict):
                    new_sec.append(req)
                    continue
                if "HTTPBearer" in req and "BearerAuth" not in req:
                    new_sec.append({"BearerAuth": req.get("HTTPBearer", [])})
                    changed = True
                else:
                    new_sec.append(req)
            if changed:
                op["security"] = new_sec


def merge_specs(specs: list[tuple[dict | None, str, str]]) -> dict:
    """
    Объединяет несколько OpenAPI-спецификаций.
    specs: список (spec_dict, path_prefix, schema_prefix).
    """
    merged_paths = {}
    merged_schemas = {}
    for spec, path_prefix, schema_prefix in specs:
        if spec is None:
            continue
        paths, schemas = _transform_spec(spec, path_prefix, schema_prefix)
        merged_paths.update(paths)
        for name, schema in schemas.items():
            if name not in merged_schemas:
                merged_schemas[name] = schema

    _add_security_to_paths(merged_paths)
    _normalize_security_scheme_names(merged_paths)

    return {
        "openapi": "3.1.0",
        "info": {
            "title": "API Gateway — все сервисы",
            "description": "Объединённая документация: Auth, Ideas, Kanban, Matching.",
            "version": "1.0.0",
        },
        "paths": merged_paths,
        "components": {
            "schemas": merged_schemas,
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                    "description": "JWT из POST /api/auth/login или POST /api/auth/register",
                }
            },
        },
    }
