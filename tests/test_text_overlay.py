from PIL import Image

from core import text_overlay


def test_mood_for_expression_matches_expected_categories():
    assert text_overlay.mood_for_expression("喜び") == "energetic"
    assert text_overlay.mood_for_expression("怒り") == "impact"
    assert text_overlay.mood_for_expression("照れ") == "shy"
    assert text_overlay.mood_for_expression("眠い") == "calm"
    assert text_overlay.mood_for_expression("驚き") == "surprise"
    assert text_overlay.mood_for_expression("びっくり") == "surprise"
    assert text_overlay.mood_for_expression("困惑") == "playful"
    assert text_overlay.mood_for_expression("お祝い") == "celebration"
    assert text_overlay.mood_for_expression("感激") == "celebration"
    assert text_overlay.mood_for_expression("決意") == "dramatic"
    assert text_overlay.mood_for_expression("未知の表情タグ") == "default"


def test_mood_for_expression_rage_takes_priority_over_plain_impact():
    # 「怒り心頭」は「怒」を含むが impact ではなく、より強い rage に分類されるべき
    assert text_overlay.mood_for_expression("怒り心頭") == "rage"
    assert text_overlay.mood_for_expression("怒り") == "impact"


def test_mood_for_expression_crying_laughter_goes_to_shy_not_energetic():
    # 「笑い泣き」は「笑」を含むが energetic ではなく shy に分類されるべき
    assert text_overlay.mood_for_expression("笑い泣き") == "shy"
    assert text_overlay.mood_for_expression("笑い") == "energetic"


def test_font_path_for_expression_points_to_existing_file():
    expressions = ["喜び", "怒り", "怒り心頭", "驚き", "困惑", "お祝い", "決意", "照れ", "眠い", "謎"]
    for expression in expressions:
        path = text_overlay.font_path_for_expression(expression)
        assert path.exists(), f"font file missing for {expression}: {path}"


def test_all_mood_fonts_exist_on_disk():
    for filename in text_overlay._MOOD_FONTS.values():
        assert (text_overlay.FONT_DIR / filename).exists(), f"missing font file: {filename}"


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
