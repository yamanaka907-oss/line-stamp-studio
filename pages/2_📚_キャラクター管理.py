"""ページ2: 保存済みキャラクターの一覧・選択・編集・削除。"""
from __future__ import annotations

import streamlit as st

from core.storage import delete_character, list_characters, update_character

st.set_page_config(page_title="キャラクター管理 | LINE Stamp Studio", page_icon="📚", layout="wide")

st.title("📚 キャラクター管理")
st.caption("保存したキャラクターの一覧です。スタンプ企画に使うキャラクターを選択してください。")

characters = list_characters()

if not characters:
    st.info("保存済みのキャラクターがありません。まずは「キャラクター生成」ページで作成してください。")
else:
    n_cols = 3
    cols = st.columns(n_cols)

    for i, character in enumerate(characters):
        with cols[i % n_cols]:
            with st.container(border=True):
                st.subheader(character.get("name", "（名称未設定）"))
                st.caption(character.get("catchphrase", ""))
                st.write(f"**ターゲット層**: {character.get('target_audience', '-')}")
                st.write(f"**モチーフ**: {character.get('motif', '-')}")
                st.write(f"**性格**: {character.get('personality', '-')}")
                with st.expander("詳細を見る"):
                    st.write(f"外見: {character.get('appearance', '')}")
                    st.write(f"性格詳細: {character.get('personality_detail', '')}")
                    st.write(f"口調: {character.get('speech_style', '')}")

                selected = st.session_state.get("selected_character_id") == character["id"]
                btn_col1, btn_col2, btn_col3 = st.columns(3)
                with btn_col1:
                    if st.button(
                        "✅ 選択中" if selected else "使う",
                        key=f"select_{character['id']}",
                        type="primary" if selected else "secondary",
                        use_container_width=True,
                    ):
                        st.session_state["selected_character_id"] = character["id"]
                        st.rerun()
                with btn_col2:
                    if st.button("✏️ 編集", key=f"edit_{character['id']}", use_container_width=True):
                        st.session_state[f"editing_{character['id']}"] = not st.session_state.get(
                            f"editing_{character['id']}", False
                        )
                        st.rerun()
                with btn_col3:
                    if st.button("🗑️ 削除", key=f"delete_{character['id']}", use_container_width=True):
                        delete_character(character["id"])
                        if st.session_state.get("selected_character_id") == character["id"]:
                            st.session_state.pop("selected_character_id", None)
                        st.rerun()

                if st.session_state.get(f"editing_{character['id']}", False):
                    with st.form(f"edit_form_{character['id']}"):
                        new_name = st.text_input("名前", value=character.get("name", ""))
                        new_catchphrase = st.text_input("キャッチコピー", value=character.get("catchphrase", ""))
                        new_appearance = st.text_area("外見の特徴", value=character.get("appearance", ""))
                        new_personality_detail = st.text_area(
                            "性格詳細", value=character.get("personality_detail", "")
                        )
                        new_speech_style = st.text_area("口調", value=character.get("speech_style", ""))
                        save_col, cancel_col = st.columns(2)
                        save_clicked = save_col.form_submit_button("💾 更新を保存", use_container_width=True)
                        cancel_clicked = cancel_col.form_submit_button("キャンセル", use_container_width=True)

                        if save_clicked:
                            update_character(
                                character["id"],
                                name=new_name,
                                catchphrase=new_catchphrase,
                                appearance=new_appearance,
                                personality_detail=new_personality_detail,
                                speech_style=new_speech_style,
                            )
                            st.session_state[f"editing_{character['id']}"] = False
                            st.success("更新しました。")
                            st.rerun()
                        if cancel_clicked:
                            st.session_state[f"editing_{character['id']}"] = False
                            st.rerun()

selected_id = st.session_state.get("selected_character_id")
if selected_id:
    st.divider()
    st.success("選択中のキャラクターで「スタンプ企画・生成」ページに進めます。")
