"""ページ1: パラメータ選択 → AIによるキャラクター設定生成。"""
from __future__ import annotations

import streamlit as st

from core.character_generator import generate_character
from core.config import MOTIF_CATEGORIES, PERSONALITY_TRAITS, TARGET_AUDIENCES
from core.storage import save_character

st.set_page_config(page_title="キャラクター生成 | LINE Stamp Studio", page_icon="🎨", layout="wide")

st.title("🎨 キャラクター生成")
st.caption("ターゲット層・モチーフ・性格を選んでAIにキャラクター設定を考えてもらいましょう。")

with st.form("character_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        target_audience = st.selectbox("ターゲット層", TARGET_AUDIENCES)
        if target_audience == "自由入力":
            target_audience = st.text_input("ターゲット層（自由入力）", value="")
    with col2:
        motif = st.selectbox("モチーフ", MOTIF_CATEGORIES)
        if motif == "自由入力":
            motif = st.text_input("モチーフ（自由入力）", value="")
    with col3:
        personality = st.selectbox("性格", PERSONALITY_TRAITS)
        if personality == "自由入力":
            personality = st.text_input("性格（自由入力）", value="")

    free_note = st.text_area("追加の要望（任意）", placeholder="例：眼鏡をかけている、方言を話す、など")
    submitted = st.form_submit_button("✨ キャラクターを生成", use_container_width=True)

if submitted:
    if not target_audience or not motif or not personality:
        st.warning("ターゲット層・モチーフ・性格をすべて入力してください。")
    else:
        with st.spinner("AIがキャラクターを考えています..."):
            character = generate_character(target_audience, motif, personality, free_note)
        character["target_audience"] = target_audience
        character["motif"] = motif
        character["personality"] = personality
        st.session_state["draft_character"] = character

draft = st.session_state.get("draft_character")
if draft:
    if draft.get("_error"):
        st.warning(f"AI生成に失敗したため、オフラインのサンプルロジックで代替表示しています: {draft['_error']}", icon="⚠️")
    elif draft.get("_offline_mock"):
        st.info("APIキー未設定のため、オフラインのサンプルロジックで生成しています。", icon="ℹ️")

    st.subheader(f"{draft.get('name')}（{draft.get('name_reading', '')}）")
    st.write(f"**キャッチコピー**: {draft.get('catchphrase', '')}")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**外見の特徴**")
        st.write(draft.get("appearance", ""))
        st.markdown("**性格**")
        st.write(draft.get("personality_detail", ""))
    with col2:
        st.markdown("**口調**")
        st.write(draft.get("speech_style", ""))
        st.markdown("**セリフ例**")
        for line in draft.get("sample_lines", []):
            st.write(f"「{line}」")

    if st.button("💾 このキャラクターを保存する", type="primary", use_container_width=True):
        saved = save_character(draft)
        st.session_state["selected_character_id"] = saved["id"]
        st.session_state.pop("draft_character", None)
        st.success(f"「{saved.get('name')}」を保存しました。「キャラクター管理」ページから確認できます。")
        st.balloons()
