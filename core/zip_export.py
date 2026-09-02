"""生成済み画像アセットを分類・整理してZIPにまとめる。"""
from __future__ import annotations

import io
import json
import zipfile
from typing import Any

from PIL import Image


def _image_bytes(image: Image.Image) -> bytes:
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()


def build_zip(
    character: dict[str, Any],
    main_image: Image.Image | None,
    tab_image: Image.Image | None,
    stamp_images: list[tuple[dict[str, Any], Image.Image]],
    metadata: dict[str, Any] | None = None,
) -> bytes:
    """main/ tab/ stamps/ フォルダに分類したZIPバイト列と、manifest.jsonを生成する。"""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        if main_image is not None:
            zf.writestr("main/main.png", _image_bytes(main_image))
        if tab_image is not None:
            zf.writestr("tab/tab.png", _image_bytes(tab_image))

        manifest: dict[str, Any] = {
            "character_name": character.get("name"),
            "stamp_count": len(stamp_images),
            "stamps": [],
        }
        for plan, img in stamp_images:
            idx = plan.get("index", 0)
            filename = f"stamps/{idx:02d}.png"
            zf.writestr(filename, _image_bytes(img))
            manifest["stamps"].append(
                {
                    "file": filename,
                    "phrase": plan.get("phrase"),
                    "expression": plan.get("expression"),
                    "pose": plan.get("pose"),
                }
            )

        if metadata:
            manifest["application_metadata"] = {k: v for k, v in metadata.items() if not k.startswith("_")}

        zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))

    buf.seek(0)
    return buf.getvalue()
