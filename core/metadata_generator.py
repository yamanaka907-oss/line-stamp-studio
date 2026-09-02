"""LINE Creators Market への申請・販売時に必要なテキスト・情報の下書きを生成する。

※本モジュールはテキストの下書きを提案するのみで、LINE Creators Marketへの自動送信・申請は行わない。
　生成された文言は申請画面へ手動でコピー＆ペーストして、内容を確認したうえで利用することを想定している。
"""
from __future__ import annotations

import json
import re
from typing import Any

from core.config import ANTHROPIC_API_KEY, TEXT_MODEL, TITLE_MAX_LEN

_SYSTEM_PROMPT = f"""あなたはLINEスタンプの販売戦略とマーケティングコピーに精通したプロデューサーです。
キャラクター設定とスタンプ内容をもとに、LINE Creators Marketへの登録申請で使う文言案を作成してください。

制約:
- title_ja / title_en は{TITLE_MAX_LEN}文字以内（審査に通りやすく、検索に強い簡潔な名前にする）
- 絵文字・機種依存文字・LINEや他社の商標を含めない
- 誇大・医療的・差別的表現を含めない

必ず次のJSON形式のみで回答してください（説明文は不要）。

{{
  "title_ja": "スタンプ名（日本語、{TITLE_MAX_LEN}文字以内）",
  "title_en": "Sticker title (English, within {TITLE_MAX_LEN} chars)",
  "promo_text_ja": "SNS等での告知に使える紹介文（日本語、120文字以内）",
  "promo_text_en": "Short promotional blurb in English (within 200 chars)",
  "search_tags": ["検索されやすいタグ候補を5個"],
  "copyright_suggestion": "コピーライト表記の構成案（例: © [発行年] [クリエイター名]）",
  "category_suggestion": "LINE Creators Marketで選ぶべきカテゴリの提案",
  "age_rating_note": "全年齢向けか年齢制限が必要かの判定コメント",
  "review_tips": ["審査に通りやすくするための確認ポイントを3つ"]
}}
"""


def _build_user_prompt(
    character: dict[str, Any],
    stamp_plan: list[dict[str, Any]],
    target_audience: str,
    creator_name: str,
) -> str:
    sample_phrases = "、".join(s.get("phrase", "") for s in stamp_plan[:8] if s.get("phrase"))
    return (
        f"キャラクター名: {character.get('name')}\n"
        f"キャッチコピー: {character.get('catchphrase')}\n"
        f"外見: {character.get('appearance')}\n"
        f"性格: {character.get('personality_detail')}\n"
        f"ターゲット層: {target_audience}\n"
        f"スタンプ枚数: {len(stamp_plan)}枚\n"
        f"収録セリフ例: {sample_phrases}\n"
        f"クリエイター名（表記用）: {creator_name or '（未入力）'}\n"
    )


def _extract_json(text: str) -> dict[str, Any]:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("AI応答からJSONを抽出できませんでした")
    return json.loads(match.group(0))


def _mock_metadata(
    character: dict[str, Any],
    stamp_plan: list[dict[str, Any]],
    target_audience: str,
    creator_name: str,
) -> dict[str, Any]:
    name = character.get("name", "キャラクター")
    creator = creator_name or "作者名"
    return {
        "title_ja": f"{name}のゆるっとスタンプ"[:TITLE_MAX_LEN],
        "title_en": f"{name} Everyday Stickers"[:TITLE_MAX_LEN],
        "promo_text_ja": f"{target_audience}に贈る、{name}のかわいい日常スタンプが登場！毎日のトークにぜひどうぞ。",
        "promo_text_en": f"Meet {name} - cute everyday stickers perfect for chatting with friends and family.",
        "search_tags": ["かわいい", "日常会話", (character.get("appearance", "")[:6] or "動物"), "ゆるい", target_audience or "日常"],
        "copyright_suggestion": f"© {creator}",
        "category_suggestion": "動物 / キャラクター（内容に応じて申請画面で選択してください）",
        "age_rating_note": "全年齢向け（暴力的・性的表現を含まないため）",
        "review_tips": [
            "背景が完全に透過されているか（白い縁やノイズが残っていないか）を確認する",
            "全スタンプでキャラクターの色・線の太さが統一されているかを確認する",
            "既存のキャラクターや商標に類似していないかを確認する",
        ],
        "_offline_mock": True,
    }


def generate_application_metadata(
    character: dict[str, Any],
    stamp_plan: list[dict[str, Any]],
    target_audience: str = "",
    creator_name: str = "",
) -> dict[str, Any]:
    if not ANTHROPIC_API_KEY:
        return _mock_metadata(character, stamp_plan, target_audience, creator_name)

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=TEXT_MODEL,
            max_tokens=1500,
            system=_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": _build_user_prompt(character, stamp_plan, target_audience, creator_name),
                }
            ],
        )
        text = "".join(block.text for block in response.content if block.type == "text")
        data = _extract_json(text)
        data["title_ja"] = data.get("title_ja", "")[:TITLE_MAX_LEN]
        data["title_en"] = data.get("title_en", "")[:TITLE_MAX_LEN]
        data["_offline_mock"] = False
        return data
    except Exception as exc:  # API障害・JSON不整合等はオフライン生成にフォールバック
        fallback = _mock_metadata(character, stamp_plan, target_audience, creator_name)
        fallback["_error"] = str(exc)
        return fallback
