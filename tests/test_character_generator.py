from core import character_generator


def test_generate_character_offline_mock_has_required_fields(monkeypatch):
    monkeypatch.setattr(character_generator, "ANTHROPIC_API_KEY", "")
    result = character_generator.generate_character("10代", "動物", "元気いっぱい", "")
    assert result["_offline_mock"] is True
    for key in ["name", "appearance", "personality_detail", "speech_style", "sample_lines"]:
        assert key in result
    assert isinstance(result["sample_lines"], list)


def test_offline_mock_speech_style_varies_by_personality(monkeypatch):
    monkeypatch.setattr(character_generator, "ANTHROPIC_API_KEY", "")
    genki = character_generator.generate_character("10代", "ゆるキャラ風", "元気いっぱい", "")
    dokuzetsu = character_generator.generate_character("10代", "ゆるキャラ風", "毒舌", "")

    assert genki["speech_style"] != dokuzetsu["speech_style"]
    assert genki["sample_lines"] != dokuzetsu["sample_lines"]


def test_offline_mock_unknown_personality_falls_back_to_default_speech_style(monkeypatch):
    monkeypatch.setattr(character_generator, "ANTHROPIC_API_KEY", "")
    result = character_generator.generate_character("10代", "動物", "自由入力の性格", "")
    assert result["speech_style"] == character_generator._DEFAULT_SPEECH_STYLE[0]


def test_offline_mock_reflects_free_note_in_appearance(monkeypatch):
    monkeypatch.setattr(character_generator, "ANTHROPIC_API_KEY", "")
    result = character_generator.generate_character("10代", "動物", "元気いっぱい", "柚子")
    assert "柚子" in result["appearance"]


def test_offline_mock_without_free_note_does_not_add_extra_text(monkeypatch):
    monkeypatch.setattr(character_generator, "ANTHROPIC_API_KEY", "")
    result = character_generator.generate_character("10代", "動物", "元気いっぱい", "")
    assert "という要望" not in result["appearance"]
