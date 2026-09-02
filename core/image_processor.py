"""背景透過・リサイズ・パディングなど画像後処理。"""
from __future__ import annotations

import io
import warnings

from PIL import Image

from core.config import MAIN_IMAGE_SIZE, STAMP_MAX_SIZE, TAB_IMAGE_SIZE


def remove_background(image: Image.Image) -> Image.Image:
    """rembgが利用可能なら背景透過処理を行う。
    未インストール時、またはモデル取得失敗等の実行時エラー時は元画像をそのまま返す。"""
    try:
        from rembg import remove
    except ImportError:
        return image.convert("RGBA")

    try:
        rgba = image.convert("RGBA")
        buf = io.BytesIO()
        rgba.save(buf, format="PNG")
        result_bytes = remove(buf.getvalue())
        return Image.open(io.BytesIO(result_bytes)).convert("RGBA")
    except Exception as exc:  # モデルダウンロード失敗等は透過なしにフォールバック
        warnings.warn(f"背景透過処理に失敗したため、元画像をそのまま使用します: {exc}")
        return image.convert("RGBA")


def fit_and_pad(image: Image.Image, target_size: tuple[int, int]) -> Image.Image:
    """アスペクト比を維持して target_size の範囲内に収め、透明背景でパディングする。"""
    image = image.convert("RGBA")
    target_w, target_h = target_size
    src_w, src_h = image.size
    scale = min(target_w / src_w, target_h / src_h)
    new_w, new_h = max(1, round(src_w * scale)), max(1, round(src_h * scale))
    resized = image.resize((new_w, new_h), Image.LANCZOS)

    canvas = Image.new("RGBA", target_size, (0, 0, 0, 0))
    offset = ((target_w - new_w) // 2, (target_h - new_h) // 2)
    canvas.paste(resized, offset, resized)
    return canvas


def _prepare(image: Image.Image, remove_bg: bool) -> Image.Image:
    return remove_background(image) if remove_bg else image.convert("RGBA")


def process_for_main(image: Image.Image, remove_bg: bool = True) -> Image.Image:
    return fit_and_pad(_prepare(image, remove_bg), MAIN_IMAGE_SIZE)


def process_for_tab(image: Image.Image, remove_bg: bool = True) -> Image.Image:
    return fit_and_pad(_prepare(image, remove_bg), TAB_IMAGE_SIZE)


def process_for_stamp(image: Image.Image, remove_bg: bool = True) -> Image.Image:
    return fit_and_pad(_prepare(image, remove_bg), STAMP_MAX_SIZE)
