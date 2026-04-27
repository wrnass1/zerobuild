from routers.match_router import _calc_match_score


def test_calc_match_score_overlap_and_missing():
    score, overlap, missing = _calc_match_score(
        required_stack=["Python", "FastAPI", "Postgres"],
        tech_stack=["python", "redis", "fastapi"],
        idea_complexity="low",
        user_level="junior",
        user_projects_count=0,
    )
    assert score > 0
    assert overlap == ["fastapi", "python"]
    assert missing == ["postgres"]


def test_calc_match_score_required_empty_is_zero():
    score, overlap, missing = _calc_match_score(
        required_stack=[],
        tech_stack=["python"],
        idea_complexity="low",
        user_level="junior",
        user_projects_count=0,
    )
    assert score == 0
    assert overlap == []
    assert missing == []

