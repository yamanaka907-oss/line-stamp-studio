"""LINE Stamp Studio — トップページ。
キャラクター考案からLINEスタンプ素材・申請情報の一括生成までを行うマルチページ Streamlit アプリ。"""
from __future__ import annotations

import streamlit as st

from core.config import ANTHROPIC_API_KEY, OPENAI_API_KEY

st.set_page_config(
    page_title="LINE Stamp Studio",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="auto",
)

st.markdown(
    """
    <style>
    /* スマートフォンなど狭い画面での余白・フォント調整 */
    @media (max-width: 640px) {
        .block-container { padding: 1rem 0.8rem 3rem 0.8rem; }
        h1 { font-size: 1.5rem !important; }
    }
    .step-card {
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🎨 LINE Stamp Studio")
st.caption("オリジナルキャラクター考案 → LINEスタンプ素材生成 → 申請情報作成 → ZIP一括出力")

st.markdown(
    "このアプリはブラウザだけで、LINEスタンプ販売に必要な一連の作業をサポートします。"
    "PC・スマートフォンどちらのブラウザからでも同じ手順で利用できます。"
)

steps = [
    ("1. 🎨 キャラクター生成", "ターゲット層・モチーフ・性格からAIがキャラクター設定を考案します。"),
    ("2. 📚 キャラクター管理", "気に入ったキャラクターをJSONに保存し、一覧から呼び出せます。"),
    ("3. 😊 スタンプ企画・生成", "セリフ・表情・ポーズを自動企画し、画像を生成→背景透過・規定サイズに自動加工します。"),
    ("4. 📝 申請情報作成", "LINE Creators Marketの申請に使えるタイトル・説明文・タグなどを自動生成します。"),
    ("5. 📦 エクスポート", "メイン・タブ・スタンプ画像と申請情報をまとめてZIPダウンロードできます。"),
]
for title, desc in steps:
    st.markdown(f'<div class="step-card"><b>{title}</b><br>{desc}</div>', unsafe_allow_html=True)

st.divider()

with st.expander("⚙️ API接続ステータス（未設定でもオフラインのモックデータで全機能を試せます）"):
    col1, col2 = st.columns(2)
    col1.metric("Anthropic API（テキスト生成）", "接続済み" if ANTHROPIC_API_KEY else "未設定 / モック動作")
    col2.metric("OpenAI Images API（画像生成）", "接続済み" if OPENAI_API_KEY else "未設定 / プレースホルダー画像")
    st.caption(
        "本番運用時は環境変数 `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` を設定してください"
        "（`.env.example` を参照）。Streamlit Community Cloud では Secrets 機能から設定できます。"
    )

st.info("左のサイドバーから各ステップのページに移動してください。", icon="👈")
