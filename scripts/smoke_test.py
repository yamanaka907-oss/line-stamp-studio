"""キャラクター生成〜ZIP出力までの一連のパイプラインをオフラインモードで検証するスモークテスト。
ブラウザを開かずに core/ 配下のロジックが一通り連携して動くことを素早く確認したいときに使う。

使い方:
    python scripts/smoke_test.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.character_generator import generate_character  # noqa: E402
from core.config import MAIN_IMAGE_SIZE, STAMP_MAX_SIZE, TAB_IMAGE_SIZE  # noqa: E402
from core.image_generator import get_image_backend  # noqa: E402
from core.image_processor import process_for_main, process_for_stamp, process_for_tab  # noqa: E402
from core.metadata_generator import generate_application_metadata  # noqa: E402
from core.stamp_planner import plan_stamp_set  # noqa: E402
from core.zip_export import build_zip  # noqa: E402


def main() -> None:
    print("1/5 キャラクター生成...")
    character = generate_character("10代", "動物", "元気いっぱい", "")
    print(f"  -> {character['name']}")

    print("2/5 スタンプ企画...")
    plan = plan_stamp_set(character, count=8, target_audience="10代")
    assert len(plan) == 8
    print(f"  -> {len(plan)}件企画")

    print("3/5 画像生成・加工（背景透過はスキップして高速確認）...")
    backend = get_image_backend()
    main_image = process_for_main(backend.generate("main icon"), remove_bg=False)
    tab_image = process_for_tab(backend.generate("tab icon"), remove_bg=False)
    stamp_images = [
        (item, process_for_stamp(backend.generate(item["image_prompt"]), remove_bg=False)) for item in plan
    ]
    assert main_image.size == MAIN_IMAGE_SIZE
    assert tab_image.size == TAB_IMAGE_SIZE
    assert all(img.size == STAMP_MAX_SIZE for _, img in stamp_images)
    print("  -> サイズ検証OK")

    print("4/5 申請情報生成...")
    metadata = generate_application_metadata(character, plan, "10代", "テスト作者")
    print(f"  -> タイトル: {metadata['title_ja']}")

    print("5/5 ZIP出力...")
    zip_bytes = build_zip(character, main_image, tab_image, stamp_images, metadata)
    print(f"  -> ZIPサイズ: {len(zip_bytes):,} bytes")

    print("\nスモークテスト成功！ core/ の一連の連携は正常に動作しています。")


if __name__ == "__main__":
    main()
