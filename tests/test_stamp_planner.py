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


def test_grid_dimensions_covers_all_stamp_count_options():
    # STAMP_COUNT_OPTIONS = [8, 16, 24, 32, 40] は全て割り切れる想定
    assert stamp_planner.grid_dimensions(8) == (2, 4)
    for count in [8, 16, 24, 32, 40]:
        rows, cols = stamp_planner.grid_dimensions(count)
        assert rows * cols == count


def test_grid_dimensions_handles_small_counts():
    assert stamp_planner.grid_dimensions(1) == (1, 1)
    assert stamp_planner.grid_dimensions(4) == (2, 2)


def test_build_sheet_prompt_mentions_every_panel_expression():
    character = {"name": "ぽてん", "appearance": "丸い"}
    batch = [
        {"expression": "喜び", "pose": "手を振る"},
        {"expression": "怒り", "pose": "腕組み"},
    ]
    prompt = stamp_planner.build_sheet_prompt(character, batch, rows=1, cols=2)
    assert "喜び" in prompt
    assert "怒り" in prompt
    assert "1x2" in prompt
    assert "2 equal-sized" in prompt
