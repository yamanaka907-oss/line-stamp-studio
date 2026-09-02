"""ページ3: スタンプ枚数指定 → AIによる企画（セリフ・表情・ポーズ・プロンプト） → 画像の準備・加工。

画像の準備は2通りから選べる:
- 手動（推奨・無料）: プロンプトをコピーしてLeonardo.ai/Bing Image Creator等に貼り付け、
  生成した画像を保存してこのページにアップロードする。
- 自動生成: OPENAI_API_KEY を設定していれば、AI画像生成APIで自動生成する（有料）。
"""
from __future__ import annotations

import streamlit as st

from core.config import MAIN_IMAGE_SIZE, STAMP_COUNT_OPTIONS, STAMP_MAX_SIZE, TAB_IMAGE_SIZE
from core.image_generator import get_image_backend
from core.image_processor import (
    load_image_file,
    process_for_main,
    process_for_stamp,
    process_for_tab,
    slice_sheet,
)
from core.stamp_planner import build_main_prompt, build_sheet_prompt, build_tab_prompt, grid_dimensions, plan_stamp_set
from core.storage import get_character, list_characters
from core.text_overlay import draw_phrase

IMAGE_TOOL_LINKS = [
    ("Gemini アプリを開く（無料・1日20枚目安）", "https://gemini.google.com/app"),
    ("Leonardo.ai を開く（Stickerプリセットあり・無料）", "https://leonardo.ai/"),
    ("Bing Image Creator を開く（DALL-E 3・無料）", "https://www.bing.com/images/create"),
    ("Ideogram を開く（文字入りデザインが得意・無料）", "https://ideogram.ai/"),
    ("Canva を開く（Magic Media・月50クレジット無料）", "https://www.canva.com/"),
]

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
    add_text = st.checkbox(
        "スタンプにセリフを文字入れする（表情に応じてフォントを自動で変更）",
        value=True,
    )
with col2:
    st.metric("メイン画像", "1枚 (240×240)")
    st.metric("タブ画像", "1枚 (96×74)")

if st.button("🧠 スタンプ内容を企画する", type="primary", use_container_width=True):
    with st.spinner("AIがセリフ・表情・ポーズを企画しています..."):
        plan = plan_stamp_set(character, count, character.get("target_audience", ""))
    st.session_state["stamp_plan"] = plan
    st.session_state["main_prompt"] = build_main_prompt(character)
    st.session_state["tab_prompt"] = build_tab_prompt(character)
    # data_editor / file_uploader の key を切り替えて、キャラクター/枚数を変えて再企画したときに
    # 古いプランの編集内容やアップロード済み画像が居座って表示され続けるのを防ぐ（Streamlitは
    # 同じkeyのウィジェットには新しく渡したvalueよりも前回のウィジェット状態を優先するため）。
    st.session_state["plan_version"] = st.session_state.get("plan_version", 0) + 1
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
        key=f"plan_editor_{st.session_state.get('plan_version', 0)}",
    )
    st.session_state["stamp_plan"] = edited_plan

    main_prompt = st.session_state.get("main_prompt", "")
    tab_prompt = st.session_state.get("tab_prompt", "")
    version = st.session_state.get("plan_version", 0)

    def finalize_stamp(raw_image, item):
        """背景透過・リサイズし、必要ならセリフを表情に応じたフォントで文字入れする。"""
        processed = process_for_stamp(raw_image, remove_bg=remove_bg)
        if add_text:
            processed = draw_phrase(processed, item.get("phrase", ""), item.get("expression", ""))
        return processed

    st.divider()
    st.subheader("画像の準備")
    source_mode = st.radio(
        "画像の取得方法",
        ["🖼️ 手動で用意する（無料・推奨）", "🤖 AI画像生成APIで自動生成（要OPENAI_API_KEY・有料）"],
        index=0,
    )

    if source_mode.startswith("🖼️"):
        st.caption("プロンプトをコピーして下のツールに貼り付け、生成した画像を保存してからアップロードしてください。")
        link_cols = st.columns(len(IMAGE_TOOL_LINKS))
        for col, (label, url) in zip(link_cols, IMAGE_TOOL_LINKS):
            col.link_button(label, url, use_container_width=True)

        st.markdown("**メイン画像 (240×240)**")
        st.code(main_prompt, language=None)
        main_file = st.file_uploader(
            "メイン画像をアップロード", type=["png", "jpg", "jpeg", "webp"], key=f"upload_main_{version}"
        )

        st.markdown("**タブ画像 (96×74)**")
        st.code(tab_prompt, language=None)
        tab_file = st.file_uploader(
            "タブ画像をアップロード", type=["png", "jpg", "jpeg", "webp"], key=f"upload_tab_{version}"
        )

        st.markdown("**スタンプ本体**")
        stamp_mode = st.radio(
            "スタンプ画像の生成方法",
            [
                "🧩 シートでまとめて生成する（推奨・無料枠を節約／キャラクターの統一感が保ちやすい）",
                "🖼️ 1枚ずつ個別に生成する（従来どおり・生成回数が多くなります）",
            ],
            index=0,
        )

        if stamp_mode.startswith("🧩"):
            st.caption(
                "複数のスタンプの表情・ポーズを1枚の画像にグリッドとしてまとめて生成し、"
                "アップロード後にアプリ側で自動的に切り分けます。生成回数が大幅に減り、"
                "同じ生成の中で描かれる分キャラクターの見た目もぶれにくくなります。"
            )
            batch_size = st.selectbox("1シートあたりの枚数", [4, 8], index=1)
            batches = [edited_plan[i : i + batch_size] for i in range(0, len(edited_plan), batch_size)]

            sheet_files = {}
            for b_idx, batch in enumerate(batches):
                rows, cols = grid_dimensions(len(batch))
                labels_text = "、".join(item.get("phrase") or item.get("expression", "") for item in batch)
                with st.expander(f"シート{b_idx + 1}（{rows}行×{cols}列・{labels_text}）", expanded=(b_idx == 0)):
                    st.code(build_sheet_prompt(character, batch, rows, cols), language=None)
                    sheet_files[b_idx] = st.file_uploader(
                        f"シート{b_idx + 1}をアップロード",
                        type=["png", "jpg", "jpeg", "webp"],
                        key=f"upload_sheet_{b_idx}_{version}",
                    )

            st.divider()
            if st.button("✅ シートを取り込む（分割・背景透過・リサイズ）", type="primary", use_container_width=True):
                missing = []
                if main_file is None:
                    missing.append("メイン画像")
                if tab_file is None:
                    missing.append("タブ画像")
                for b_idx in range(len(batches)):
                    if sheet_files.get(b_idx) is None:
                        missing.append(f"シート{b_idx + 1}")

                if missing:
                    st.warning("次の画像が未アップロードです: " + "、".join(missing))
                else:
                    progress = st.progress(0.0, text="画像を処理中...")
                    total_steps = len(batches) + 2

                    main_image = process_for_main(load_image_file(main_file), remove_bg=remove_bg)
                    progress.progress(1 / total_steps, text="メイン画像を処理中...")
                    tab_image = process_for_tab(load_image_file(tab_file), remove_bg=remove_bg)
                    progress.progress(2 / total_steps, text="タブ画像を処理中...")

                    stamp_images = []
                    for b_idx, batch in enumerate(batches):
                        progress.progress(
                            (b_idx + 3) / total_steps, text=f"シート {b_idx + 1}/{len(batches)} を処理中..."
                        )
                        rows, cols = grid_dimensions(len(batch))
                        cells = slice_sheet(load_image_file(sheet_files[b_idx]), rows, cols)
                        for item, cell in zip(batch, cells):
                            stamp_images.append((item, finalize_stamp(cell, item)))

                    progress.progress(1.0, text="完了！")
                    st.session_state["generated_assets"] = {
                        "main": main_image,
                        "tab": tab_image,
                        "stamps": stamp_images,
                    }
                    st.success("画像の取り込み・分割・背景透過・リサイズが完了しました。")
        else:
            stamp_files = {}
            for item in edited_plan:
                idx = item["index"]
                with st.expander(f"{idx}. {item.get('phrase') or '（セリフなし）'} ／ {item.get('expression', '')}"):
                    st.code(item.get("image_prompt", ""), language=None)
                    stamp_files[idx] = st.file_uploader(
                        f"スタンプ{idx}の画像をアップロード",
                        type=["png", "jpg", "jpeg", "webp"],
                        key=f"upload_stamp_{idx}_{version}",
                    )

            st.divider()
            if st.button("✅ アップロード画像を取り込む（背景透過・リサイズ）", type="primary", use_container_width=True):
                missing = []
                if main_file is None:
                    missing.append("メイン画像")
                if tab_file is None:
                    missing.append("タブ画像")
                for item in edited_plan:
                    if stamp_files.get(item["index"]) is None:
                        missing.append(f"スタンプ{item['index']}")

                if missing:
                    st.warning("次の画像が未アップロードです: " + "、".join(missing))
                else:
                    progress = st.progress(0.0, text="画像を処理中...")
                    total_steps = len(edited_plan) + 2

                    main_image = process_for_main(load_image_file(main_file), remove_bg=remove_bg)
                    progress.progress(1 / total_steps, text="メイン画像を処理中...")
                    tab_image = process_for_tab(load_image_file(tab_file), remove_bg=remove_bg)
                    progress.progress(2 / total_steps, text="タブ画像を処理中...")

                    stamp_images = []
                    for i, item in enumerate(edited_plan):
                        progress.progress(
                            (i + 3) / total_steps, text=f"スタンプ {i + 1}/{len(edited_plan)} を処理中..."
                        )
                        img = load_image_file(stamp_files[item["index"]])
                        stamp_images.append((item, finalize_stamp(img, item)))

                    progress.progress(1.0, text="完了！")
                    st.session_state["generated_assets"] = {
                        "main": main_image,
                        "tab": tab_image,
                        "stamps": stamp_images,
                    }
                    st.success("画像の取り込み・背景透過・リサイズが完了しました。")
    else:
        if st.button("🖼️ 画像を生成する（メイン・タブ・スタンプ全て）", type="primary", use_container_width=True):
            backend = get_image_backend()
            progress = st.progress(0.0, text="準備中...")
            total_steps = len(edited_plan) + 2

            progress.progress(1 / total_steps, text="メイン画像を生成中...")
            main_image = process_for_main(backend.generate(main_prompt, size=MAIN_IMAGE_SIZE), remove_bg=remove_bg)

            progress.progress(2 / total_steps, text="タブ画像を生成中...")
            tab_image = process_for_tab(backend.generate(tab_prompt, size=TAB_IMAGE_SIZE), remove_bg=remove_bg)

            stamp_images = []
            for i, item in enumerate(edited_plan):
                progress.progress((i + 3) / total_steps, text=f"スタンプ {i + 1}/{len(edited_plan)} を生成中...")
                raw = backend.generate(item["image_prompt"], size=STAMP_MAX_SIZE)
                stamp_images.append((item, finalize_stamp(raw, item)))

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
