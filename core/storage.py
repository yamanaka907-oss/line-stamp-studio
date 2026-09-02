"""キャラクター設定の永続化（JSONファイルベース）。
将来的にSQLite等のDBへ差し替えやすいよう、単純なリポジトリ関数の集まりにしている。"""
from __future__ import annotations

import json
import threading
import uuid
from datetime import datetime, timezone
from typing import Any

from core.config import CHARACTERS_FILE

_lock = threading.Lock()


def _read_all_locked() -> list[dict[str, Any]]:
    """呼び出し側が _lock を保持している前提の内部ヘルパー。"""
    if not CHARACTERS_FILE.exists():
        return []
    try:
        return json.loads(CHARACTERS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _write_all_locked(items: list[dict[str, Any]]) -> None:
    """呼び出し側が _lock を保持している前提の内部ヘルパー。"""
    CHARACTERS_FILE.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def list_characters() -> list[dict[str, Any]]:
    with _lock:
        items = _read_all_locked()
    return sorted(items, key=lambda c: c.get("created_at", ""), reverse=True)


def get_character(character_id: str) -> dict[str, Any] | None:
    with _lock:
        items = _read_all_locked()
    for c in items:
        if c["id"] == character_id:
            return c
    return None


def save_character(character: dict[str, Any]) -> dict[str, Any]:
    character = dict(character)
    character.setdefault("id", str(uuid.uuid4()))
    character.setdefault("created_at", datetime.now(timezone.utc).isoformat())
    # 読み込み〜書き込みを1つのロックで囲み、複数タブ/セッションからの同時保存で
    # 片方の変更がもう片方に上書きされて消える競合状態を防ぐ。
    with _lock:
        items = _read_all_locked()
        items.append(character)
        _write_all_locked(items)
    return character


def update_character(character_id: str, **fields: Any) -> dict[str, Any] | None:
    with _lock:
        items = _read_all_locked()
        for c in items:
            if c["id"] == character_id:
                c.update(fields)
                c["updated_at"] = datetime.now(timezone.utc).isoformat()
                _write_all_locked(items)
                return c
    return None


def delete_character(character_id: str) -> bool:
    with _lock:
        items = _read_all_locked()
        remaining = [c for c in items if c["id"] != character_id]
        if len(remaining) == len(items):
            return False
        _write_all_locked(remaining)
    return True
