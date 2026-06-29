import builtins

import pytest

import webcam


def test_supports_capture_with_plain_capabilities():
    assert webcam.supports_capture(webcam.V4L2_CAP_VIDEO_CAPTURE, 0) is True


def test_supports_capture_uses_device_caps_when_available():
    capabilities = webcam.V4L2_CAP_DEVICE_CAPS
    device_caps = webcam.V4L2_CAP_VIDEO_CAPTURE
    assert webcam.supports_capture(capabilities, device_caps) is True


def test_supports_capture_false_for_metadata_only_node():
    assert webcam.supports_capture(0, webcam.V4L2_CAP_VIDEO_CAPTURE) is False


def test_device_name_reads_sysfs(monkeypatch):
    class FakeFile:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return 'Integrated Camera\n'

    monkeypatch.setattr(builtins, 'open', lambda *args, **kwargs: FakeFile())

    assert webcam.device_name(0) == 'Integrated Camera'


def test_device_name_falls_back_to_path_on_error(monkeypatch):
    def raise_oserror(*args, **kwargs):
        raise OSError

    monkeypatch.setattr(builtins, 'open', raise_oserror)

    assert webcam.device_name(2) == '/dev/video2'


def test_deduplicate_keeps_highest_resolution_per_name():
    devices = [
        (2, 'Logitech BRIO', (4096, 2160)),
        (4, 'Logitech BRIO', (340, 340)),
        (0, 'ACER HD', (1280, 720)),
    ]

    assert webcam.deduplicate(devices) == [
        (0, 'ACER HD', (1280, 720)),
        (2, 'Logitech BRIO', (4096, 2160)),
    ]


def test_deduplicate_keeps_lowest_index_on_resolution_tie():
    devices = [
        (4, 'Logitech BRIO', (1920, 1080)),
        (2, 'Logitech BRIO', (1920, 1080)),
    ]

    assert webcam.deduplicate(devices) == [(2, 'Logitech BRIO', (1920, 1080))]


def test_deduplicate_handles_unknown_resolution():
    devices = [(0, 'Cam', None), (1, 'Cam', (640, 480))]

    assert webcam.deduplicate(devices) == [(1, 'Cam', (640, 480))]


def test_format_resolution_known():
    assert webcam.format_resolution((1920, 1080)) == '1920x1080'


def test_format_resolution_unknown():
    assert webcam.format_resolution(None) == 'unknown'


def test_select_device_returns_preferred_without_probing():
    assert webcam.select_device(preferred=3) == 3


def test_select_device_returns_single_available(monkeypatch):
    monkeypatch.setattr(webcam, 'list_devices', lambda: [(1, 'Integrated Camera', (1280, 720))])

    assert webcam.select_device() == 1


def test_select_device_raises_when_none_available(monkeypatch):
    monkeypatch.setattr(webcam, 'list_devices', lambda: [])

    with pytest.raises(RuntimeError):
        webcam.select_device()


def test_select_device_prompts_until_valid_choice(monkeypatch):
    devices = [(0, 'Front', (640, 480)), (2, 'Back', (1280, 720))]
    monkeypatch.setattr(webcam, 'list_devices', lambda: devices)
    answers = iter(['9', 'x', '2'])
    monkeypatch.setattr(builtins, 'input', lambda _: next(answers))

    assert webcam.select_device() == 2


def test_frame_interval_for_thirty_fps():
    assert webcam.frame_interval(30) == 33


def test_frame_interval_for_one_fps():
    assert webcam.frame_interval(1) == 1000


def test_frame_interval_clamps_to_at_least_one_millisecond():
    assert webcam.frame_interval(100000) == 1


def test_frame_interval_handles_non_positive_fps():
    assert webcam.frame_interval(0) == 1000


def test_compute_cell_aspect_from_pixels():
    assert webcam.compute_cell_aspect(48, 160, 1280, 768) == pytest.approx(2.0)


def test_compute_cell_aspect_falls_back_when_pixels_missing():
    assert webcam.compute_cell_aspect(48, 160, 0, 0, default=2) == 2


def test_terminal_size_parses_stty_output(monkeypatch):
    class FakeStream:
        def read(self):
            return '24 80'

    monkeypatch.setattr(webcam.os, 'popen', lambda *args, **kwargs: FakeStream())

    assert webcam.terminal_size() == (24, 80)
