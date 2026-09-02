"""アプリ全体で共有する設定値・定数。"""
from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CHARACTERS_FILE = DATA_DIR / "characters.json"
GENERATED_DIR = DATA_DIR / "generated"

DATA_DIR.mkdir(parents=True, exist_ok=True)
GENERATED_DIR.mkdir(parents=True, exist_ok=True)

# --- LINEスタンプ公式規定サイズ (px) ---
MAIN_IMAGE_SIZE = (240, 240)      # メイン画像
TAB_IMAGE_SIZE = (96, 74)         # タブ（チャットルーム一覧用）画像
STAMP_MAX_SIZE = (370, 320)       # スタンプ画像の最大バウンディングボックス

STAMP_COUNT_OPTIONS = [8, 16, 24, 32, 40]

# --- キャラクター生成の選択肢 ---
TARGET_AUDIENCES = [
    "10代", "20代女性", "20代男性", "30〜40代ファミリー",
    "ビジネスパーソン", "シニア層", "ペット好き", "地域・観光PR", "自由入力",
]
MOTIF_CATEGORIES = [
    "動物", "特産品・グルメ", "ゆるキャラ風", "植物・花",
    "ファンタジー", "乗り物", "自由入力",
]
PERSONALITY_TRAITS = [
    "元気いっぱい", "のんびり癒し系", "ツンデレ", "毒舌", "甘えん坊",
    "クールでミステリアス", "おっちょこちょい", "自由入力",
]

DEFAULT_EXPRESSIONS = [
    "喜び", "笑い", "怒り", "悲しみ", "驚き", "照れ",
    "困惑", "眠い", "やる気", "感謝", "お願い", "拍手",
    "了解", "ありがとう", "ごめんね", "おはよう", "おやすみ", "考え中",
    "拍手喝采", "がんばる", "ハート", "お祝い", "疑問", "バイバイ",
    "応援", "ダメ出し", "祝福", "スタンバイ", "リラックス", "びっくり",
    "笑い泣き", "決意", "落ち込み", "自慢げ", "ウインク", "拍手２",
    "眠気MAX", "ときめき", "怒り心頭", "感激",
]

# --- LINE Creators Market 申請メタデータ関連 ---
TITLE_MAX_LEN = 40          # スタンプ名の上限文字数の目安
RECOMMENDED_TAG_COUNT = 5

# --- API keys（環境変数 / Streamlit secrets / .env から読み込み） ---
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
TEXT_MODEL = os.environ.get("ANTHROPIC_TEXT_MODEL", "claude-sonnet-5")
IMAGE_MODEL = os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-1")
