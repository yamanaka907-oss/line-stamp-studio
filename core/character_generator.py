"""キャラクター設定（名前・外見特徴・口調など）をAIで動的生成する。"""
from __future__ import annotations

import json
import random
import re
from typing import Any

from core.config import ANTHROPIC_API_KEY, TEXT_MODEL

_SYSTEM_PROMPT = """あなたはLINEスタンプ用オリジナルキャラクターの企画を専門とするクリエイティブディレクターです。
依頼された条件に基づき、愛されるキャラクター設定を1つ考案し、必ず次のJSON形式のみで回答してください（説明文や前後の文章は一切不要）。

{
  "name": "キャラクターの名前",
  "name_reading": "ひらがな読み",
  "catchphrase": "一言キャッチコピー（20文字以内）",
  "appearance": "外見の特徴（色・体型・服装・小物など、画像生成に使える具体的な描写）",
  "personality_detail": "性格の詳細説明（2〜3文）",
  "speech_style": "口調・話し方の特徴（語尾や一人称など）",
  "sample_lines": ["口調が伝わる短いセリフ例を3つ"]
}
"""


def _build_user_prompt(target_audience: str, motif: str, personality: str, free_note: str) -> str:
    parts = [
        f"ターゲット層: {target_audience}",
        f"モチーフ: {motif}",
        f"性格の方向性: {personality}",
    ]
    if free_note:
        parts.append(f"追加の要望: {free_note}")
    return "以下の条件でキャラクターを1体考案してください。\n" + "\n".join(parts)


def _extract_json(text: str) -> dict[str, Any]:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("AI応答からJSONを抽出できませんでした")
    return json.loads(match.group(0))


# 性格ごとに口調・セリフ例を変える（オフラインモック用）。一覧は core/config.py の
# PERSONALITY_TRAITS と対応させているが、一致しない値（自由入力等）は _DEFAULT_SPEECH_STYLE を使う。
_PERSONALITY_SPEECH_STYLES: dict[str, tuple[str, list[str]]] = {
    "元気いっぱい": (
        "語尾に「〜だよ」「〜なのだ」をつける、明るく元気な口調。",
        ["今日もいっしょにがんばろうね！", "えへへ、うれしいのだ〜", "ちょっとひとやすみ、しよ？"],
    ),
    "のんびり癒し系": (
        "「〜だねぇ」「〜なのねぇ」とゆったり伸ばす、癒し系の口調。",
        ["まあ、のんびりいこうねぇ。", "ふわぁ〜、きもちいいねぇ。", "むりしなくていいんだよぉ。"],
    ),
    "ツンデレ": (
        "「べ、別に〜だし」「〜なんだからね」という、素直になれない口調。",
        ["べ、別にあんたのためじゃないんだからね！", "…ちょっとだけ、うれしいかも。", "勘違いしないでよね！"],
    ),
    "毒舌": (
        "「〜でしょ」「〜なんだけど」と、遠慮なくズバズバ言う口調。",
        ["はぁ？それマジで言ってんの？", "まあ、悪くはないんじゃない。", "しっかりしなよ、まったく。"],
    ),
    "甘えん坊": (
        "語尾に「〜だもん」「〜なの」をつける、甘えた口調。",
        ["ねえねえ、かまってほしいの〜。", "だいすき！ぎゅーして？", "ひとりはさみしいんだもん。"],
    ),
    "クールでミステリアス": (
        "感情を表に出さない、短く落ち着いた口調。",
        ["……そう。", "興味深いな。", "また会おう。"],
    ),
    "おっちょこちょい": (
        "「〜あわわ」「〜しちゃった」と、あわてん坊な口調。",
        ["あっ、また転んじゃった…！", "えーっと、えーっと…あわわ！", "だ、大丈夫、たぶん平気！"],
    ),
}
_DEFAULT_SPEECH_STYLE: tuple[str, list[str]] = (
    "語尾に「〜だよ」「〜なのだ」をつける、親しみやすい口調。",
    ["今日もいっしょにがんばろうね！", "えへへ、うれしいのだ〜", "ちょっとひとやすみ、しよ？"],
)


def _mock_generate(target_audience: str, motif: str, personality: str, free_note: str) -> dict[str, Any]:
    """APIキー未設定時のオフライン用フォールバック（デモ動作確認向け）。"""
    base_names = ["まる", "ぽて", "ころん", "むぎ", "ふわり", "ぴよ"]
    name = random.choice(base_names) + random.choice(["ちゃん", "くん", "ん"])
    speech_style, sample_lines = _PERSONALITY_SPEECH_STYLES.get(personality, _DEFAULT_SPEECH_STYLE)

    appearance = (
        f"{motif}をモチーフにした丸みのあるフォルム。パステルカラーの体で、"
        f"{personality}な雰囲気が伝わる大きな瞳が特徴。"
    )
    if free_note:
        appearance += f" また「{free_note}」という要望も取り入れている。"

    return {
        "name": name,
        "name_reading": name,
        "catchphrase": f"{motif}生まれの{personality}な{name}です！",
        "appearance": appearance,
        "personality_detail": (
            f"{target_audience}に親しみやすい{personality}な性格。"
            "感情表現が豊かで、見る人を自然と笑顔にする。"
        ),
        "speech_style": speech_style,
        "sample_lines": list(sample_lines),
        "_offline_mock": True,
    }


def generate_character(
    target_audience: str,
    motif: str,
    personality: str,
    free_note: str = "",
) -> dict[str, Any]:
    """AI APIでキャラクター設定を生成する。
    APIキー未設定時、またはAPI呼び出し/応答解析に失敗した場合はオフラインモックにフォールバックする。"""
    if not ANTHROPIC_API_KEY:
        return _mock_generate(target_audience, motif, personality, free_note)

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=TEXT_MODEL,
            max_tokens=1024,
            system=_SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": _build_user_prompt(target_audience, motif, personality, free_note)}
            ],
        )
        text = "".join(block.text for block in response.content if block.type == "text")
        data = _extract_json(text)
        data["_offline_mock"] = False
        return data
    except Exception as exc:  # API障害・JSON不整合等はオフライン生成にフォールバック
        fallback = _mock_generate(target_audience, motif, personality, free_note)
        fallback["_error"] = str(exc)
        return fallback
