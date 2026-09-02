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


def _read_all() -> list[dict[str, Any]]:
    if not CHARACTERS_FILE.exists():
        return []
    with _lock:
        try:
            return json.loads(CHARACTERS_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []


def _write_all(items: list[dict[str, Any]]) -> None:
    with _lock:
        CHARACTERS_FILE.write_text(
            json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8"
        )


def list_characters() -> list[dict[str, Any]]:
    return sorted(_read_all(), key=lambda c: c.get("created_at", ""), reverse=True)


def get_character(character_id: str) -> dict[str, Any] | None:
    for c in _read_all():
        if c["id"] == character_id:
            return c
    return None


def save_character(character: dict[str, Any]) -> dict[str, Any]:
    items = _read_all()
    character = dict(character)
    character.setdefault("id", str(uuid.uuid4()))
    character.setdefault("created_at", datetime.now(timezone.utc).isoformat())
    items.append(character)
    _write_all(items)
    return character


def update_character(character_id: str, **fields: Any) -> dict[str, Any] | None:
    items = _read_all()
    for c in items:
        if c["id"] == character_id:
            c.update(fields)
            c["updated_at"] = datetime.now(timezone.utc).isoformat()
            _write_all(items)
            return c
    return None


def delete_character(character_id: str) -> bool:
    items = _read_all()
    remaining = [c for c in items if c["id"] != character_id]
    if len(remaining) == len(items):
        return False
    _write_all(remaining)
    return True
