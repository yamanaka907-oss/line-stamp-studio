from core import stamp_planner


def test_plan_stamp_set_offline_mock_returns_requested_count(monkeypatch):
    monkeypatch.setattr(stamp_planner, "ANTHROPIC_API_KEY", "")
    character = {"name": "テスト", "appearance": "丸い", "personality_detail": "元気"}
    plan = stamp_planner.plan_stamp_set(character, count=8)
    assert len(plan) == 8
    assert [item["index"] for item in plan] == list(range(1, 9))
    for item in plan:
        assert item["phrase"]
        assert item["image_prompt"]


def test_plan_stamp_set_offline_mock_handles_count_larger_than_default_expressions(monkeypatch):
    monkeypatch.setattr(stamp_planner, "ANTHROPIC_API_KEY", "")
    character = {"name": "テスト"}
    plan = stamp_planner.plan_stamp_set(character, count=40)
    assert len(plan) == 40
