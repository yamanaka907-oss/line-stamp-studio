"""スタンプ画像へのセリフ文字入れ。表情のムードに応じてフォントを切り替える。"""
from __future__ import annotations

import warnings
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from core.config import BASE_DIR

FONT_DIR = BASE_DIR / "assets" / "fonts"

# 表情の雰囲気ごとに使うフォント。表情の判定は完全一致ではなくキーワード部分一致で行うため、
# core.config.DEFAULT_EXPRESSIONS にない自由記述の表情（AI生成時）にもある程度対応できる。
# 目を引くよう、丸ゴシック・インパクト系・筆文字系・ポップ系など幅を持たせている。
_MOOD_FONTS: dict[str, str] = {
    "rage": "RampartOne-Regular.ttf",  # 激怒（グラフィティ風の極太フォント）
    "impact": "ReggaeOne-Regular.ttf",  # 怒り・ダメ出しなど強い感情
    "surprise": "DelaGothicOne-Regular.ttf",  # 驚き・びっくり（重量感のあるインパクトフォント）
    "playful": "HachiMaruPop-Regular.ttf",  # 疑問・困惑などポップで愛らしい感情
    "celebration": "YujiSyuku-Regular.ttf",  # お祝い・祝福など（筆文字風）
    "dramatic": "YujiBoku-Regular.ttf",  # 決意など力強い場面（太めの筆文字風）
    "shy": "Yomogi-Regular.ttf",  # 照れ・悲しみなど繊細な感情（手書き風）
    "calm": "ZenMaruGothic-Regular.ttf",  # 眠い・のんびりなど穏やかな感情
    "energetic": "KosugiMaru-Regular.ttf",  # 喜び・元気など明るい感情
    "default": "NotoSansJP-Regular.ttf",
}

# 辞書の順序 = 判定の優先順位（例:「怒り心頭」は先に rage で判定され、
# 後段の impact の「怒」キーワードには回らない）。
_MOOD_KEYWORDS: dict[str, tuple[str, ...]] = {
    "rage": ("怒り心頭",),
    "impact": ("怒", "ダメ"),
    "surprise": ("驚", "びっくり"),
    "playful": ("疑問", "困惑"),
    "celebration": ("お祝い", "祝福", "感激", "ハート"),
    "dramatic": ("決意",),
    "shy": ("照れ", "悲し", "ごめん", "落ち込", "お願い", "甘え", "ウインク", "ときめき", "自慢げ", "笑い泣き"),
    "calm": ("眠", "おやすみ", "考え中", "スタンバイ", "リラックス", "クール", "ミステリアス"),
    "energetic": ("喜", "笑", "やる気", "感謝", "拍手", "ありがとう", "おはよう", "がんばる", "応援", "了解", "バイバイ"),
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
