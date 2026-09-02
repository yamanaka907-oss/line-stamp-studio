from core import character_generator


def test_generate_character_offline_mock_has_required_fields(monkeypatch):
    monkeypatch.setattr(character_generator, "ANTHROPIC_API_KEY", "")
    result = character_generator.generate_character("10代", "動物", "元気いっぱい", "")
    assert result["_offline_mock"] is True
    for key in ["name", "appearance", "personality_detail", "speech_style", "sample_lines"]:
        assert key in result
    assert isinstance(result["sample_lines"], list)
