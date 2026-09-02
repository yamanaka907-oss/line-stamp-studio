"""スタンプ画像へのセリフ文字入れ。表情のムードに応じてフォントを切り替える。"""
from __future__ import annotations

import warnings
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from core.config import BASE_DIR

FONT_DIR = BASE_DIR / "assets" / "fonts"

# 表情の雰囲気ごとに使うフォント。表情の判定は完全一致ではなくキーワード部分一致で行うため、
# core.config.DEFAULT_EXPRESSIONS にない自由記述の表情（AI生成時）にもある程度対応できる。
_MOOD_FONTS: dict[str, str] = {
    "impact": "ReggaeOne-Regular.ttf",  # 怒り・驚きなど強い感情
    "shy": "Yomogi-Regular.ttf",  # 照れ・悲しみなど繊細な感情
    "calm": "ZenMaruGothic-Regular.ttf",  # 眠い・のんびりなど穏やかな感情
    "energetic": "KosugiMaru-Regular.ttf",  # 喜び・元気など明るい感情
    "default": "NotoSansJP-Regular.ttf",
}

_MOOD_KEYWORDS: dict[str, tuple[str, ...]] = {
    "impact": ("怒", "ダメ", "疑問", "困惑", "驚", "びっくり"),
    "shy": ("照れ", "悲し", "ごめん", "落ち込", "お願い", "甘え"),
    "calm": ("眠", "おやすみ", "考え中", "スタンバイ", "リラックス", "ウインク", "クール", "ミステリアス"),
    "energetic": (
        "喜", "笑", "やる気", "感謝", "拍手", "ありがとう", "おはよう", "がんばる",
        "ハート", "お祝い", "応援", "祝福", "決意", "自慢げ", "ときめき", "感激", "了解", "バイバイ",
    ),
}


def mood_for_expression(expression: str) -> str:
    """表情の文字列から、キーワード一致でムード区分（フォント選択用）を判定する。"""
    for mood, keywords in _MOOD_KEYWORDS.items():
        if any(keyword in expression for keyword in keywords):
            return mood
    return "default"


def font_path_for_expression(expression: str) -> Path:
    return FONT_DIR / _MOOD_FONTS[mood_for_expression(expression)]


def draw_phrase(image: Image.Image, phrase: str, expression: str = "") -> Image.Image:
    """スタンプ画像下部にセリフを描き込む。フォントは表情のムードに応じて変える。
    セリフが空、またはフォントファイルが見つからない場合は元画像をそのまま返す。"""
    if not phrase:
        return image

    font_path = font_path_for_expression(expression)
    if not font_path.exists():
        warnings.warn(f"フォントファイルが見つからないため文字入れをスキップします: {font_path}")
        return image

    image = image.convert("RGBA")
    draw = ImageDraw.Draw(image)
    width, height = image.size

    font_size = max(12, height // 6)
    font = ImageFont.truetype(str(font_path), font_size)
    bbox = draw.textbbox((0, 0), phrase, font=font)
    text_w = bbox[2] - bbox[0]

    # 横幅に収まらない場合はフォントサイズを縮小する
    while text_w > width * 0.9 and font_size > 10:
        font_size -= 2
        font = ImageFont.truetype(str(font_path), font_size)
        bbox = draw.textbbox((0, 0), phrase, font=font)
        text_w = bbox[2] - bbox[0]

    text_h = bbox[3] - bbox[1]
    x = (width - text_w) / 2 - bbox[0]
    y = height - text_h - bbox[1] - max(4, height * 0.04)

    stroke_width = max(2, font_size // 12)
    draw.text(
        (x, y),
        phrase,
        font=font,
        fill=(40, 40, 40, 255),
        stroke_width=stroke_width,
        stroke_fill=(255, 255, 255, 255),
    )
    return image
