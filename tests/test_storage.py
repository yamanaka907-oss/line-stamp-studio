import concurrent.futures

from core import storage


def test_save_list_get_update_delete_character(monkeypatch, tmp_path):
    monkeypatch.setattr(storage, "CHARACTERS_FILE", tmp_path / "characters.json")

    saved = storage.save_character({"name": "テスト太郎"})
    assert saved["id"]
    assert saved["created_at"]

    listed = storage.list_characters()
    assert len(listed) == 1
    assert listed[0]["name"] == "テスト太郎"

    fetched = storage.get_character(saved["id"])
    assert fetched["name"] == "テスト太郎"

    updated = storage.update_character(saved["id"], name="テスト次郎")
    assert updated["name"] == "テスト次郎"
    assert "updated_at" in updated

    assert storage.delete_character(saved["id"]) is True
    assert storage.list_characters() == []
    assert storage.delete_character(saved["id"]) is False


def test_get_character_missing_returns_none(monkeypatch, tmp_path):
    monkeypatch.setattr(storage, "CHARACTERS_FILE", tmp_path / "characters.json")
    assert storage.get_character("does-not-exist") is None


def test_update_character_missing_returns_none(monkeypatch, tmp_path):
    monkeypatch.setattr(storage, "CHARACTERS_FILE", tmp_path / "characters.json")
    assert storage.update_character("does-not-exist", name="x") is None


def test_list_characters_orders_newest_first(monkeypatch, tmp_path):
    monkeypatch.setattr(storage, "CHARACTERS_FILE", tmp_path / "characters.json")
    first = storage.save_character({"name": "先輩", "created_at": "2026-01-01T00:00:00+00:00"})
    second = storage.save_character({"name": "後輩", "created_at": "2026-06-01T00:00:00+00:00"})
    ordered = storage.list_characters()
    assert [c["id"] for c in ordered] == [second["id"], first["id"]]


def test_read_all_survives_corrupted_json_file(monkeypatch, tmp_path):
    characters_file = tmp_path / "characters.json"
    characters_file.write_text("{not valid json", encoding="utf-8")
    monkeypatch.setattr(storage, "CHARACTERS_FILE", characters_file)

    assert storage.list_characters() == []


def test_concurrent_saves_do_not_lose_writes(monkeypatch, tmp_path):
    # 複数タブ/セッションから同時に保存しても、read-modify-writeの競合で
    # 互いの書き込みを消し合わないことを確認する回帰テスト。
    monkeypatch.setattr(storage, "CHARACTERS_FILE", tmp_path / "characters.json")

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(storage.save_character, {"name": f"キャラ{i}"}) for i in range(20)]
        for f in futures:
            f.result()

    assert len(storage.list_characters()) == 20
