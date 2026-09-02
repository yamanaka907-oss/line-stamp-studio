from core import metadata_generator
from core.config import TITLE_MAX_LEN


def test_generate_application_metadata_offline_mock_respects_title_length(monkeypatch):
    monkeypatch.setattr(metadata_generator, "ANTHROPIC_API_KEY", "")
    character = {"name": "とても長い名前のキャラクターですよこれは", "target_audience": "10代"}
    stamp_plan = [{"phrase": "おはよう"}, {"phrase": "ありがとう"}]
    metadata = metadata_generator.generate_application_metadata(character, stamp_plan, "10代", "作者")
    assert len(metadata["title_ja"]) <= TITLE_MAX_LEN
    assert len(metadata["title_en"]) <= TITLE_MAX_LEN
    assert metadata["_offline_mock"] is True
    assert "review_tips" in metadata
