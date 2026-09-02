import io
import json
import zipfile

from PIL import Image

from core.zip_export import build_zip


def test_build_zip_structure_and_manifest():
    main_img = Image.new("RGBA", (240, 240), (255, 0, 0, 255))
    tab_img = Image.new("RGBA", (96, 74), (0, 255, 0, 255))
    stamp_img = Image.new("RGBA", (370, 320), (0, 0, 255, 255))
    plan_item = {"index": 1, "phrase": "やあ", "expression": "笑い", "pose": "手を振る"}

    zip_bytes = build_zip(
        character={"name": "テストキャラ"},
        main_image=main_img,
        tab_image=tab_img,
        stamp_images=[(plan_item, stamp_img)],
        metadata={"title_ja": "タイトル", "_offline_mock": True},
    )

    zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    names = zf.namelist()
    assert "main/main.png" in names
    assert "tab/tab.png" in names
    assert "stamps/01.png" in names
    assert "manifest.json" in names

    manifest = json.loads(zf.read("manifest.json"))
    assert manifest["character_name"] == "テストキャラ"
    assert manifest["stamp_count"] == 1
    assert manifest["stamps"][0]["phrase"] == "やあ"
    assert "_offline_mock" not in manifest["application_metadata"]


def test_build_zip_without_main_or_tab_still_succeeds():
    stamp_img = Image.new("RGBA", (370, 320), (0, 0, 255, 255))
    zip_bytes = build_zip(
        character={"name": "テストキャラ"},
        main_image=None,
        tab_image=None,
        stamp_images=[({"index": 1}, stamp_img)],
    )
    zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    assert "main/main.png" not in zf.namelist()
    assert "stamps/01.png" in zf.namelist()
