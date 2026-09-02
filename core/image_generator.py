"""画像生成バックエンドの抽象化。
OpenAI Images API を既定の実装としつつ、APIキー未設定時はプレースホルダー画像を生成する。
Stability AI 等へ差し替えたい場合は ImageBackend を実装したクラスを追加し、get_image_backend() を変更する。"""
from __future__ import annotations

import base64
import hashlib
import io
from abc import ABC, abstractmethod

from PIL import Image, ImageDraw, ImageFont

from core.config import IMAGE_MODEL, OPENAI_API_KEY


class ImageBackend(ABC):
    @abstractmethod
    def generate(self, prompt: str, size: tuple[int, int] = (1024, 1024)) -> Image.Image:
        ...


class OpenAIImageBackend(ImageBackend):
    def __init__(self, api_key: str, model: str = IMAGE_MODEL):
        import openai

        self._client = openai.OpenAI(api_key=api_key)
        self._model = model

    def _size_string_for(self, size: tuple[int, int]) -> str:
        """要求された縦横比に最も近い、モデルがサポートするサイズ文字列を選ぶ。
        最終的なピクセルサイズは image_processor.fit_and_pad が調整するため、
        ここでは向き（正方形・横長・縦長）の指定精度で十分。"""
        w, h = size
        if w == h:
            return "1024x1024"
        landscape = w > h
        if self._model == "gpt-image-1":
            return "1536x1024" if landscape else "1024x1536"
        if self._model.startswith("dall-e-3"):
            return "1792x1024" if landscape else "1024x1792"
        # dall-e-2 等、正方形しかサポートしないモデル向けのフォールバック
        return "1024x1024"

    def generate(self, prompt: str, size: tuple[int, int] = (1024, 1024)) -> Image.Image:
        kwargs = {"model": self._model, "prompt": prompt, "size": self._size_string_for(size), "n": 1}
        if self._model != "gpt-image-1":
            # dall-e-2 / dall-e-3 は response_format を明示しないと url 形式で返るため、
            # 常に b64_json を要求する（gpt-image-1 はこのパラメータ自体を受け付けない）。
            kwargs["response_format"] = "b64_json"

        result = self._client.images.generate(**kwargs)
        item = result.data[0]
        if getattr(item, "b64_json", None):
            return Image.open(io.BytesIO(base64.b64decode(item.b64_json))).convert("RGBA")

        # フォールバック: url でしか返らないモデル/設定の場合はダウンロードする
        import urllib.request

        with urllib.request.urlopen(item.url) as response:
            return Image.open(io.BytesIO(response.read())).convert("RGBA")


class PlaceholderImageBackend(ImageBackend):
    """APIキー未設定時のオフライン動作確認用。プロンプトから決定的に
    パステルカラーのプレースホルダー画像（アイコン＋ラベル）を生成する。"""

    _PALETTE = [
        (255, 209, 220), (255, 234, 167), (200, 230, 255),
        (210, 255, 220), (230, 210, 255), (255, 220, 200),
    ]

    def generate(self, prompt: str, size: tuple[int, int] = (1024, 1024)) -> Image.Image:
        seed = int(hashlib.sha256(prompt.encode("utf-8")).hexdigest(), 16)
        color = self._PALETTE[seed % len(self._PALETTE)]
        img = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        margin = int(min(size) * 0.08)
        draw.ellipse(
            [margin, margin, size[0] - margin, size[1] - margin],
            fill=color + (255,),
            outline=(90, 90, 90, 255),
            width=max(4, min(size) // 60),
        )
        label = prompt.split(",")[0][:18] or "STAMP"
        try:
            font = ImageFont.truetype("arial.ttf", size=max(18, min(size) // 12))
        except OSError:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), label, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(
            ((size[0] - tw) / 2, (size[1] - th) / 2),
            label,
            fill=(70, 70, 70, 255),
            font=font,
        )
        return img


def get_image_backend() -> ImageBackend:
    if OPENAI_API_KEY:
        return OpenAIImageBackend(api_key=OPENAI_API_KEY)
    return PlaceholderImageBackend()
