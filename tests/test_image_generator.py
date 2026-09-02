from core import image_generator
from core.image_generator import PlaceholderImageBackend, get_image_backend


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
