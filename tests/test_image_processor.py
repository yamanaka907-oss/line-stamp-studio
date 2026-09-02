import io

from PIL import Image

from core import image_processor
from core.config import MAIN_IMAGE_SIZE, STAMP_MAX_SIZE, TAB_IMAGE_SIZE


def test_fit_and_pad_produces_exact_target_size_for_various_aspect_ratios():
    for src_size in [(500, 500), (1024, 300), (200, 800)]:
        img = Image.new("RGBA", src_size, (255, 0, 0, 255))
        result = image_processor.fit_and_pad(img, STAMP_MAX_SIZE)
        assert result.size == STAMP_MAX_SIZE
        assert result.mode == "RGBA"


def test_fit_and_pad_pads_with_transparency_not_content():
    # 縦長画像を横長キャンバスに収めると、左右に透明な余白ができるはず
    img = Image.new("RGBA", (100, 400), (0, 255, 0, 255))
    result = image_processor.fit_and_pad(img, (370, 320))
    top_left_alpha = result.getpixel((0, 0))[3]
    center_alpha = result.getpixel((result.width // 2, result.height // 2))[3]
    assert top_left_alpha == 0
    assert center_alpha == 255


def test_remove_background_without_rembg_returns_rgba_unchanged():
    img = Image.new("RGB", (50, 50), (10, 20, 30))
    result = image_processor.remove_background(img)
    assert result.mode == "RGBA"
    assert result.size == (50, 50)


def test_process_for_main_tab_stamp_sizes():
    img = Image.new("RGBA", (300, 300), (1, 2, 3, 255))
    assert image_processor.process_for_main(img).size == MAIN_IMAGE_SIZE
    assert image_processor.process_for_tab(img).size == TAB_IMAGE_SIZE
    assert image_processor.process_for_stamp(img).size == STAMP_MAX_SIZE


def test_process_for_main_remove_bg_false_still_matches_target_size():
    img = Image.new("RGBA", (300, 300), (1, 2, 3, 255))
    result = image_processor.process_for_main(img, remove_bg=False)
    assert result.size == MAIN_IMAGE_SIZE


def test_slice_sheet_splits_into_correct_count_and_reading_order():
    # 2行×4列のシート。各セルを行/列インデックスをエンコードした色で塗り分けて
    # 読み順（左上→右へ、行ごとに下へ）が正しいことを検証する。
    rows, cols = 2, 4
    cell_size = 50
    sheet = Image.new("RGBA", (cell_size * cols, cell_size * rows))
    for r in range(rows):
        for c in range(cols):
            color = (r * 50, c * 30, 0, 255)
            for x in range(c * cell_size, (c + 1) * cell_size):
                for y in range(r * cell_size, (r + 1) * cell_size):
                    sheet.putpixel((x, y), color)

    cells = image_processor.slice_sheet(sheet, rows, cols)
    assert len(cells) == rows * cols

    idx = 0
    for r in range(rows):
        for c in range(cols):
            expected_color = (r * 50, c * 30, 0, 255)
            assert cells[idx].getpixel((5, 5)) == expected_color
            idx += 1


def test_slice_sheet_cells_cover_full_image_dimensions():
    sheet = Image.new("RGBA", (400, 200), (1, 2, 3, 255))
    cells = image_processor.slice_sheet(sheet, rows=2, cols=4)
    # 各セルはおおよそ同じサイズで、端数は最後の行/列に吸収される
    assert all(c.width in (100,) for c in cells)
    assert all(c.height in (100,) for c in cells)


def test_load_image_file_reads_uploaded_png_as_rgba():
    buf = io.BytesIO()
    Image.new("RGB", (64, 48), (10, 20, 30)).save(buf, format="PNG")
    buf.seek(0)

    loaded = image_processor.load_image_file(buf)
    assert loaded.mode == "RGBA"
    assert loaded.size == (64, 48)
