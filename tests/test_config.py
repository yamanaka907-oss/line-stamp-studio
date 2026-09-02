from core import config


def test_line_sticker_official_sizes():
    assert config.MAIN_IMAGE_SIZE == (240, 240)
    assert config.TAB_IMAGE_SIZE == (96, 74)
    assert config.STAMP_MAX_SIZE == (370, 320)


def test_stamp_count_options_are_sorted_and_positive():
    assert config.STAMP_COUNT_OPTIONS == sorted(config.STAMP_COUNT_OPTIONS)
    assert all(n > 0 for n in config.STAMP_COUNT_OPTIONS)
