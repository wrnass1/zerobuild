from openapi_merge import merge_specs


def test_merge_specs_adds_security_and_normalizes_scheme_names():
    spec = {
        "openapi": "3.1.0",
        "paths": {
            "/tasks/{task_id}": {
                "get": {
                    "summary": "Get",
                    "security": [{"HTTPBearer": []}],
                }
            }
        },
        "components": {"schemas": {}},
    }

    merged = merge_specs([(spec, "/api/kanban", "Kanban_")])
    op = merged["paths"]["/api/kanban/tasks/{task_id}"]["get"]
    assert op["security"] == [{"BearerAuth": []}]
    assert "BearerAuth" in merged["components"]["securitySchemes"]

