"""キャラクター情報から LINEスタンプ一式（セリフ・ポーズ・表情・画像生成プロンプト）を企画する。"""
from __future__ import annotations

import json
import re
from typing import Any

from core.config import ANTHROPIC_API_KEY, DEFAULT_EXPRESSIONS, TEXT_MODEL

_SYSTEM_PROMPT = """あなたはLINEスタンプの企画・シナリオライターです。
与えられたキャラクター設定とターゲット層をもとに、指定枚数分のスタンプ案を考案してください。
日常のトーク（挨拶・感謝・了解・お願い・お祝いなど）で幅広く使えるバリエーションにし、
表情・ポーズ・セリフが重複しないようにしてください。
必ず次のJSON配列のみで回答してください（説明文は不要）。

[
  {
    "index": 1,
    "phrase": "スタンプに載せる短いセリフ（10文字前後、空文字も可）",
    "expression": "表情（例: 喜び、驚き、困惑 など）",
    "pose": "ポーズ・仕草の説明",
    "image_prompt": "画像生成AI向けの英語プロンプト。キャラクターの外見・ポーズ・表情・背景なし・LINEスタンプ風のフラットで縁取りのあるイラストスタイルを明記すること"
  }
]
"""


def _build_user_prompt(character: dict[str, Any], count: int, target_audience: str) -> str:
    return (
        f"キャラクター名: {character.get('name')}\n"
        f"外見: {character.get('appearance')}\n"
        f"性格: {character.get('personality_detail')}\n"
        f"口調: {character.get('speech_style')}\n"
        f"ターゲット層: {target_audience}\n"
        f"必要なスタンプ枚数: {count}枚\n"
    )


def _extract_json_array(text: str) -> list[dict[str, Any]]:
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if not match:
        raise ValueError("AI応答からJSON配列を抽出できませんでした")
    return json.loads(match.group(0))


def _mock_plan(character: dict[str, Any], count: int) -> list[dict[str, Any]]:
    name = character.get("name", "キャラクター")
    phrases = [
        "おはよう！", "ありがとう", "了解です", "ごめんね", "お疲れさま",
        "だいすき", "がんばる！", "おやすみ〜", "やったー！", "また今度",
        "ちょっと待って", "OK!", "ふぅ…", "うれしい！", "びっくり！",
        "祝・完了", "ヘルプ！", "考え中…", "拍手！", "いいね！",
        "ないしょ", "こまった〜", "はじめまして", "バイバイ", "ラブ！",
        "そうだね", "がんばって", "おめでとう", "しんぱいしないで", "ぎゅー",
        "おなかすいた", "ねむい…", "げんき？", "よろしくね", "だいじょうぶ",
        "きょうもいい日", "ひとやすみ", "了解しました", "楽しみ！", "また明日",
    ]
    expressions = (DEFAULT_EXPRESSIONS * ((count // len(DEFAULT_EXPRESSIONS)) + 1))[:count]
    plan = []
    for i in range(count):
        phrase = phrases[i % len(phrases)]
        expression = expressions[i]
        plan.append(
            {
                "index": i + 1,
                "phrase": phrase,
                "expression": expression,
                "pose": f"{expression}を表現するポーズ",
                "image_prompt": (
                    f"cute flat-color sticker illustration of a character named {name}, "
                    f"appearance: {character.get('appearance', '')}, "
                    f"expression: {expression}, showing {expression} emotion, "
                    "thick clean outline, no background, LINE sticker style, centered composition"
                ),
            }
        )
    return plan


def build_main_prompt(character: dict[str, Any]) -> str:
    """メイン画像（240×240）用の画像生成プロンプトを組み立てる。
    Gemini等の画像生成AIにそのままコピー＆ペーストして使える形式。"""
    return (
        f"LINE sticker main icon, cute flat-color illustration of {character.get('name')}, "
        f"appearance: {character.get('appearance', '')}, friendly smiling pose, thick outline, "
        "no background, centered"
    )


def build_tab_prompt(character: dict[str, Any]) -> str:
    """タブ画像（96×74）用の画像生成プロンプトを組み立てる。"""
    return build_main_prompt(character) + ", simple close-up face only, works at very small size"


def grid_dimensions(count: int) -> tuple[int, int]:
    """count枚を並べるのに適した (行数, 列数) を返す。可能な限り正方形に近い約数の組を選ぶ。
    シート1枚あたりの生成回数（＝無料枠の消費）を抑えつつ、AIが1枚の画像内で
    描き分けやすいレイアウトにするため。"""
    if count <= 1:
        return 1, max(1, count)
    rows = max(1, round(count**0.5))
    while rows > 1 and count % rows != 0:
        rows -= 1
    cols = count // rows
    return rows, cols


def build_sheet_prompt(character: dict[str, Any], batch: list[dict[str, Any]], rows: int, cols: int) -> str:
    """複数スタンプ分の表情・ポーズを1枚のグリッドシートとして生成するためのプロンプトを組み立てる。
    生成後は core.image_processor.slice_sheet() で読み順にセルへ切り出す想定。"""
    panel_lines = " ".join(
        f"Panel {i}: expression {item.get('expression', '')}, pose: {item.get('pose', '')}."
        for i, item in enumerate(batch, start=1)
    )
    return (
        f"A character reference sheet, {rows}x{cols} grid layout with exactly {len(batch)} equal-sized "
        f"square panels arranged in {rows} rows and {cols} columns (read left-to-right, top-to-bottom), "
        "thin white gutters between panels, flat-color sticker illustration style, thick clean outline, "
        f"plain white background per panel, of a character named {character.get('name')}, appearance: "
        f"{character.get('appearance', '')}. Keep the character's design, proportions, and color palette "
        f"perfectly consistent across every panel. {panel_lines}"
    )


def plan_stamp_set(
    character: dict[str, Any],
    count: int,
    target_audience: str = "",
) -> list[dict[str, Any]]:
    """AI APIでスタンプ企画を生成する。
    APIキー未設定時、またはAPI呼び出し/応答解析に失敗した場合はオフラインモックにフォールバックする。"""
    if not ANTHROPIC_API_KEY:
        return _mock_plan(character, count)

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=TEXT_MODEL,
            max_tokens=4096,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": _build_user_prompt(character, count, target_audience)}],
        )
        text = "".join(block.text for block in response.content if block.type == "text")
        plan = _extract_json_array(text)
        return plan[:count]
    except Exception:  # API障害・JSON不整合等はオフライン企画にフォールバック
        return _mock_plan(character, count)
