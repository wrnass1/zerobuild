from main import get_upstream


def test_get_upstream_routes_to_services():
    assert get_upstream("/api/auth/login")[0].endswith("auth.up")
    assert get_upstream("/api/ideas/ideas/1")[0].endswith("ideas.up")
    assert get_upstream("/api/kanban/boards/1")[0].endswith("kanban.up")
    assert get_upstream("/api/match/match/1")[0].endswith("match.up")

