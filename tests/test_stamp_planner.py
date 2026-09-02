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


def test_build_main_prompt_includes_character_name_and_appearance():
    character = {"name": "ぽてん", "appearance": "丸くてパステルカラー"}
    prompt = stamp_planner.build_main_prompt(character)
    assert "ぽてん" in prompt
    assert "丸くてパステルカラー" in prompt


def test_build_tab_prompt_extends_main_prompt():
    character = {"name": "ぽてん", "appearance": "丸い"}
    main_prompt = stamp_planner.build_main_prompt(character)
    tab_prompt = stamp_planner.build_tab_prompt(character)
    assert tab_prompt.startswith(main_prompt)
    assert tab_prompt != main_prompt
