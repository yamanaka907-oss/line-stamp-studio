from PIL import Image

from core import text_overlay


def test_mood_for_expression_matches_expected_categories():
    assert text_overlay.mood_for_expression("喜び") == "energetic"
    assert text_overlay.mood_for_expression("怒り") == "impact"
    assert text_overlay.mood_for_expression("照れ") == "shy"
    assert text_overlay.mood_for_expression("眠い") == "calm"
    assert text_overlay.mood_for_expression("未知の表情タグ") == "default"


def test_font_path_for_expression_points_to_existing_file():
    for expression in ["喜び", "怒り", "照れ", "眠い", "謎"]:
        path = text_overlay.font_path_for_expression(expression)
        assert path.exists(), f"font file missing for {expression}: {path}"


def test_draw_phrase_skips_empty_phrase():
    img = Image.new("RGBA", (370, 320), (200, 220, 255, 255))
    result = text_overlay.draw_phrase(img, "", "喜び")
    assert result.tobytes() == img.tobytes()


def test_draw_phrase_modifies_pixels_when_phrase_given():
    img = Image.new("RGBA", (370, 320), (200, 220, 255, 255))
    result = text_overlay.draw_phrase(img, "おはよう！", "喜び")
    assert result.size == img.size
    assert result.tobytes() != img.tobytes()


def test_draw_phrase_shrinks_long_text_to_fit_width():
    img = Image.new("RGBA", (370, 320), (255, 255, 255, 255))
    long_phrase = "しんぱいしないでね、だいじょうぶだよ"
    result = text_overlay.draw_phrase(img, long_phrase, "照れ")
    # 何かが描画されており、かつ画像サイズは変わらないこと
    assert result.size == (370, 320)
    assert result.tobytes() != img.tobytes()


def test_draw_phrase_returns_original_when_font_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(text_overlay, "FONT_DIR", tmp_path)
    img = Image.new("RGBA", (370, 320), (200, 220, 255, 255))
    result = text_overlay.draw_phrase(img, "おはよう！", "喜び")
    assert result.tobytes() == img.tobytes()
