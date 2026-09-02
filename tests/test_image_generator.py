from core import image_generator
from core.image_generator import OpenAIImageBackend, PlaceholderImageBackend, get_image_backend


def _backend_with_model(model: str) -> OpenAIImageBackend:
    # openaiパッケージ未インストールでもテストできるよう、__init__を経由せず
    # _model 属性だけを持つインスタンスを作る（_size_string_forはそれ以外に依存しない）。
    backend = OpenAIImageBackend.__new__(OpenAIImageBackend)
    backend._model = model
    return backend


def test_placeholder_backend_generates_expected_size_and_mode():
    backend = PlaceholderImageBackend()
    img = backend.generate("cute animal character", size=(512, 512))
    assert img.size == (512, 512)
    assert img.mode == "RGBA"


def test_placeholder_backend_is_deterministic_for_same_prompt():
    backend = PlaceholderImageBackend()
    img1 = backend.generate("same prompt")
    img2 = backend.generate("same prompt")
    assert img1.tobytes() == img2.tobytes()


def test_placeholder_backend_varies_color_by_prompt():
    backend = PlaceholderImageBackend()
    img1 = backend.generate("happy expression")
    img2 = backend.generate("angry expression")
    assert img1.tobytes() != img2.tobytes()


def test_get_image_backend_without_api_key_returns_placeholder(monkeypatch):
    monkeypatch.setattr(image_generator, "OPENAI_API_KEY", "")
    assert isinstance(get_image_backend(), PlaceholderImageBackend)


def test_size_string_for_square_is_always_square():
    backend = _backend_with_model("gpt-image-1")
    assert backend._size_string_for((240, 240)) == "1024x1024"


def test_size_string_for_gpt_image_1_matches_orientation():
    backend = _backend_with_model("gpt-image-1")
    assert backend._size_string_for((370, 320)) == "1536x1024"  # landscape
    assert backend._size_string_for((240, 400)) == "1024x1536"  # portrait


def test_size_string_for_dalle3_uses_its_own_presets():
    backend = _backend_with_model("dall-e-3")
    assert backend._size_string_for((1200, 800)) == "1792x1024"
    assert backend._size_string_for((800, 1200)) == "1024x1792"


def test_size_string_for_dalle2_only_supports_square():
    backend = _backend_with_model("dall-e-2")
    assert backend._size_string_for((800, 400)) == "1024x1024"
