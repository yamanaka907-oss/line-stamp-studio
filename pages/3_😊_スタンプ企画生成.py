"""ページ3: スタンプ枚数指定 → AIによる企画（セリフ・表情・ポーズ・プロンプト） → 画像生成・加工。"""
from __future__ import annotations

import streamlit as st

from core.config import STAMP_COUNT_OPTIONS
from core.image_generator import get_image_backend
from core.image_processor import process_for_main, process_for_stamp, process_for_tab
from core.stamp_planner import plan_stamp_set
from core.storage import get_character, list_characters

st.set_page_config(page_title="スタンプ企画・生成 | LINE Stamp Studio", page_icon="😊", layout="wide")

st.title("😊 スタンプ企画・生成")

characters = list_characters()
if not characters:
    st.warning("先に「キャラクター生成」でキャラクターを作成・保存してください。")
    st.stop()

name_to_id = {f"{c['name']}（{c.get('motif', '')}）": c["id"] for c in characters}
labels = list(name_to_id.keys())
default_id = st.session_state.get("selected_character_id")
default_label = next((k for k, v in name_to_id.items() if v == default_id), labels[0])

selected_label = st.selectbox("キャラクターを選択", labels, index=labels.index(default_label))
character = get_character(name_to_id[selected_label])
st.session_state["selected_character_id"] = character["id"]

col1, col2 = st.columns([2, 1])
with col1:
    count = st.select_slider("スタンプ枚数", options=STAMP_COUNT_OPTIONS, value=8)
    remove_bg = st.checkbox(
        "背景透過を行う（rembg使用・初回はモデル取得のため数十秒かかる場合があります）",
        value=True,
    )
with col2:
    st.metric("メイン画像", "1枚 (240×240)")
    st.metric("タブ画像", "1枚 (96×74)")

if st.button("🧠 スタンプ内容を企画する", type="primary", use_container_width=True):
    with st.spinner("AIがセリフ・表情・ポーズを企画しています..."):
        plan = plan_stamp_set(character, count, character.get("target_audience", ""))
    st.session_state["stamp_plan"] = plan
    st.session_state.pop("generated_assets", None)

plan = st.session_state.get("stamp_plan")
if plan:
    st.subheader("企画内容（編集可能）")
    edited_plan = st.data_editor(
        plan,
        column_config={
            "index": st.column_config.NumberColumn("No.", disabled=True),
            "phrase": st.column_config.TextColumn("セリフ"),
            "expression": st.column_config.TextColumn("表情"),
            "pose": st.column_config.TextColumn("ポーズ"),
            "image_prompt": st.column_config.TextColumn("画像生成プロンプト", width="large"),
        },
        use_container_width=True,
        num_rows="fixed",
        key="plan_editor",
    )
    st.session_state["stamp_plan"] = edited_plan

    st.divider()
    if st.button("🖼️ 画像を生成する（メイン・タブ・スタンプ全て）", type="primary", use_container_width=True):
        backend = get_image_backend()
        progress = st.progress(0.0, text="準備中...")
        total_steps = len(edited_plan) + 2

        main_prompt = (
            f"LINE sticker main icon, cute flat-color illustration of {character.get('name')}, "
            f"appearance: {character.get('appearance', '')}, friendly smiling pose, thick outline, "
            "no background, centered"
        )
        progress.progress(1 / total_steps, text="メイン画像を生成中...")
        main_image = process_for_main(backend.generate(main_prompt), remove_bg=remove_bg)

        tab_prompt = main_prompt + ", simple close-up face only, works at very small size"
        progress.progress(2 / total_steps, text="タブ画像を生成中...")
        tab_image = process_for_tab(backend.generate(tab_prompt), remove_bg=remove_bg)

        stamp_images = []
        for i, item in enumerate(edited_plan):
            progress.progress((i + 3) / total_steps, text=f"スタンプ {i + 1}/{len(edited_plan)} を生成中...")
            raw = backend.generate(item["image_prompt"])
            stamp_images.append((item, process_for_stamp(raw, remove_bg=remove_bg)))

        progress.progress(1.0, text="完了！")
        st.session_state["generated_assets"] = {
            "main": main_image,
            "tab": tab_image,
            "stamps": stamp_images,
        }
        st.success("画像の生成・背景透過・リサイズが完了しました。")

assets = st.session_state.get("generated_assets")
if assets:
    st.divider()
    st.subheader("プレビュー")
    c1, c2 = st.columns(2)
    c1.image(assets["main"], caption="メイン画像 240×240")
    c2.image(assets["tab"], caption="タブ画像 96×74")

    st.markdown("**スタンプ本体**")
    n_cols = 4
    cols = st.columns(n_cols)
    for i, (plan_item, img) in enumerate(assets["stamps"]):
        with cols[i % n_cols]:
            st.image(img, caption=f"{plan_item.get('index')}. {plan_item.get('phrase', '')}")

    st.info(
        "「申請情報作成」ページでLINE Creators Market向けのテキストを作成し、"
        "「エクスポート」ページでZIPをダウンロードできます。",
        icon="➡️",
    )
