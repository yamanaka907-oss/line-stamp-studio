"""ページ5: 生成済みのメイン・タブ・スタンプ画像＋申請情報をZIPにまとめてダウンロード。"""
from __future__ import annotations

from datetime import datetime

import streamlit as st

from core.storage import get_character
from core.zip_export import build_zip

st.set_page_config(page_title="エクスポート | LINE Stamp Studio", page_icon="📦", layout="wide")

st.title("📦 エクスポート")

character_id = st.session_state.get("selected_character_id")
character = get_character(character_id) if character_id else None
assets = st.session_state.get("generated_assets")
metadata = st.session_state.get("application_metadata")

if not character or not assets:
    st.warning("先に「スタンプ企画・生成」で画像を生成してください。")
    st.stop()

st.write(f"**キャラクター**: {character.get('name')}")
st.write(f"**スタンプ枚数**: {len(assets['stamps'])}枚")
st.write(f"**申請情報**: {'作成済み' if metadata else '未作成（未同梱でも出力可能）'}")

zip_bytes = build_zip(
    character=character,
    main_image=assets.get("main"),
    tab_image=assets.get("tab"),
    stamp_images=assets.get("stamps", []),
    metadata=metadata,
)

filename = f"{character.get('name', 'line_stamp')}_{datetime.now().strftime('%Y%m%d_%H%M')}.zip"

st.download_button(
    "⬇️ ZIPを一括ダウンロード",
    data=zip_bytes,
    file_name=filename,
    mime="application/zip",
    type="primary",
    use_container_width=True,
)

st.caption(
    "ZIP内は main/（メイン画像）・tab/（タブ画像）・stamps/（スタンプ本体）に分類され、"
    "manifest.json にセリフ・表情・申請情報を含めています。"
)
