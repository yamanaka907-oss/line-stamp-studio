"""ページ4: LINE Creators Marketへの申請・販売に必要なテキスト情報の下書きを生成する。

※本ページはテキストの下書きを作成するのみで、LINE Creators Marketへの自動申請・送信は行いません。
　生成された文言は各自でLINE Creators Marketの申請画面へコピー＆ペーストしてご利用ください。
"""
from __future__ import annotations

import streamlit as st

from core.metadata_generator import generate_application_metadata
from core.storage import get_character

st.set_page_config(page_title="申請情報作成 | LINE Stamp Studio", page_icon="📝", layout="wide")

st.title("📝 申請情報作成（LINE Creators Market向け）")
st.caption(
    "スタンプタイトル・紹介文・タグ・コピーライト表記などの下書きを自動生成します。"
    "内容は必ずご自身で確認のうえ、申請画面に貼り付けてご利用ください。"
)

character_id = st.session_state.get("selected_character_id")
character = get_character(character_id) if character_id else None
stamp_plan = st.session_state.get("stamp_plan")

if not character:
    st.warning("先に「キャラクター生成」または「キャラクター管理」でキャラクターを選択してください。")
    st.stop()
if not stamp_plan:
    st.warning("先に「スタンプ企画・生成」でスタンプ内容を企画してください。")
    st.stop()

creator_name = st.text_input("クリエイター名（コピーライト表記に使用）", value=st.session_state.get("creator_name", ""))
st.session_state["creator_name"] = creator_name

if st.button("📝 申請情報を生成する", type="primary", use_container_width=True):
    with st.spinner("申請用テキストを作成しています..."):
        metadata = generate_application_metadata(
            character, stamp_plan, character.get("target_audience", ""), creator_name
        )
    st.session_state["application_metadata"] = metadata

metadata = st.session_state.get("application_metadata")
if metadata:
    if metadata.get("_error"):
        st.warning(f"AI生成に失敗したため、オフラインのサンプルロジックで代替表示しています: {metadata['_error']}", icon="⚠️")
    elif metadata.get("_offline_mock"):
        st.info("APIキー未設定のため、オフラインのサンプルロジックで生成しています。", icon="ℹ️")

    st.subheader("スタンプタイトル")
    col1, col2 = st.columns(2)
    with col1:
        st.caption(f"日本語（{len(metadata.get('title_ja', ''))}/40文字）")
        st.code(metadata.get("title_ja", ""), language=None)
    with col2:
        st.caption(f"英語（{len(metadata.get('title_en', ''))}/40 chars）")
        st.code(metadata.get("title_en", ""), language=None)

    st.subheader("紹介文（SNS告知・補足用）")
    st.code(metadata.get("promo_text_ja", ""), language=None)
    st.code(metadata.get("promo_text_en", ""), language=None)

    st.subheader("検索タグ候補")
    st.code(", ".join(metadata.get("search_tags", [])), language=None)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("コピーライト表記案")
        st.code(metadata.get("copyright_suggestion", ""), language=None)
        st.subheader("カテゴリ提案")
        st.write(metadata.get("category_suggestion", ""))
    with col4:
        st.subheader("年齢制限の目安")
        st.write(metadata.get("age_rating_note", ""))
        st.subheader("審査対策チェックポイント")
        for tip in metadata.get("review_tips", []):
            st.write(f"- {tip}")

    st.divider()
    st.caption("各コードブロック右上のコピーアイコンから、申請画面へワンクリックでコピーできます。")
