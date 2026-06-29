"""Shared runtime: webcam selection and the curses render loop."""

import contextlib
import curses
import fcntl
import glob
import os
import struct
import sys

import cv2

from ascii_art import CELL_ASPECT_RATIO, crop_square, iter_cells, square_extent

ESCAPE_KEY = 27
DEFAULT_FPS = 30

VIDIOC_QUERYCAP = 0x80685600
VIDIOC_ENUM_FMT = 0xC0405602
VIDIOC_ENUM_FRAMESIZES = 0xC02C564A
V4L2_CAP_VIDEO_CAPTURE = 0x00000001
V4L2_CAP_DEVICE_CAPS = 0x80000000
V4L2_BUF_TYPE_VIDEO_CAPTURE = 1
V4L2_FRMSIZE_TYPE_DISCRETE = 1
TIOCGWINSZ = 0x5413


@contextlib.contextmanager
def suppressed_stderr():  # pragma: no cover
    """Silence C-level stderr (OpenCV/V4L2/FFMPEG noise) within the block."""
    saved_stderr = os.dup(2)
    devnull = os.open(os.devnull, os.O_WRONLY)
    try:
        os.dup2(devnull, 2)
        yield
    finally:
        os.dup2(saved_stderr, 2)
        os.close(devnull)
        os.close(saved_stderr)


def supports_capture(capabilities, device_caps):
    """Return True when the V4L2 capabilities expose a video capture node."""
    caps = device_caps if capabilities & V4L2_CAP_DEVICE_CAPS else capabilities
    return bool(caps & V4L2_CAP_VIDEO_CAPTURE)


def is_capture_device(path):  # pragma: no cover
    """Return True when the V4L2 node at `path` can capture video."""
    try:
        with open(path, 'rb', buffering=0) as device:
            buffer = bytearray(104)
            fcntl.ioctl(device, VIDIOC_QUERYCAP, buffer)
    except OSError:
        return False

    capabilities, device_caps = struct.unpack_from('<II', buffer, 84)
    return supports_capture(capabilities, device_caps)


def device_name(index):
    """Return the human-readable name of a webcam, or its device path."""
    try:
        with open(f'/sys/class/video4linux/video{index}/name') as handle:
            return handle.read().strip()
    except OSError:
        return f'/dev/video{index}'


def max_resolution(path):  # pragma: no cover
    """Return the largest (width, height) a V4L2 node supports, or None."""
    best = None
    best_area = -1

    try:
        with open(path, 'rb', buffering=0) as device:
            for format_index in range(64):
                descriptor = bytearray(64)
                struct.pack_into('<II', descriptor, 0, format_index, V4L2_BUF_TYPE_VIDEO_CAPTURE)
                try:
                    fcntl.ioctl(device, VIDIOC_ENUM_FMT, descriptor)
                except OSError:
                    break

                pixel_format = struct.unpack_from('<I', descriptor, 44)[0]

                for size_index in range(128):
                    frame_size = bytearray(44)
                    struct.pack_into('<II', frame_size, 0, size_index, pixel_format)
                    try:
                        fcntl.ioctl(device, VIDIOC_ENUM_FRAMESIZES, frame_size)
                    except OSError:
                        break

                    size_type = struct.unpack_from('<I', frame_size, 8)[0]
                    if size_type == V4L2_FRMSIZE_TYPE_DISCRETE:
                        width, height = struct.unpack_from('<II', frame_size, 12)
                    else:
                        width = struct.unpack_from('<I', frame_size, 16)[0]
                        height = struct.unpack_from('<I', frame_size, 24)[0]

                    area = width * height
                    if area > best_area:
                        best_area = area
                        best = (width, height)
    except OSError:
        return None

    return best


def deduplicate(devices):
    """Keep the highest-resolution node per camera name, ordered by index."""
    best = {}

    for index, name, resolution in sorted(devices, key=lambda device: device[0]):
        area = resolution[0] * resolution[1] if resolution else -1
        current = best.get(name)
        if current is None or area > current[1]:
            best[name] = ((index, name, resolution), area)

    return sorted((device for device, _ in best.values()), key=lambda device: device[0])


def list_devices():  # pragma: no cover
    """Return [(index, name, resolution)] for every webcam, deduplicated by name."""
    indices = sorted(
        int(path.removeprefix('/dev/video'))
        for path in glob.glob('/dev/video*')
        if path.removeprefix('/dev/video').isdigit()
    )
    devices = [
        (index, device_name(index), max_resolution(f'/dev/video{index}'))
        for index in indices
        if is_capture_device(f'/dev/video{index}')
    ]
    return deduplicate(devices)


def format_resolution(resolution):
    """Return a printable label for a (width, height) resolution."""
    if resolution is None:
        return 'unknown'
    return f'{resolution[0]}x{resolution[1]}'


def select_device(preferred=None):
    """Pick a webcam index, prompting the user when several are available."""
    if preferred is not None:
        return preferred

    devices = list_devices()

    if not devices:
        raise RuntimeError('No webcam found.')

    if len(devices) == 1:
        return devices[0][0]

    print('Available webcams:')
    for index, name, resolution in devices:
        print(f'  [{index}] {name} ({format_resolution(resolution)})')

    valid = {index for index, _, _ in devices}
    while True:
        choice = input('Select a webcam index: ').strip()
        if choice.isdigit() and int(choice) in valid:
            return int(choice)
        print('Invalid choice, try again.')


def terminal_size():
    """Return the (rows, columns) of the current terminal."""
    rows, columns = map(int, os.popen('stty size', 'r').read().split())
    return rows, columns


def frame_interval(fps):
    """Return the per-frame delay in milliseconds for a target FPS."""
    if fps <= 0:
        return 1000
    return max(1, int(1000 / fps))


def compute_cell_aspect(rows, columns, x_pixels, y_pixels, default=CELL_ASPECT_RATIO):
    """Return the cell height/width ratio from a terminal's pixel dimensions."""
    if not all((rows, columns, x_pixels, y_pixels)):
        return default
    return (y_pixels * columns) / (x_pixels * rows)


def cell_aspect_ratio(default=CELL_ASPECT_RATIO):  # pragma: no cover
    """Measure the terminal cell height/width ratio, falling back to `default`."""
    try:
        packed = fcntl.ioctl(sys.stdout, TIOCGWINSZ, struct.pack('HHHH', 0, 0, 0, 0))
    except OSError:
        return default
    rows, columns, x_pixels, y_pixels = struct.unpack('HHHH', packed)
    return compute_cell_aspect(rows, columns, x_pixels, y_pixels, default)


def run(draw, device=None, setup=None, cell_aspect=None, fps=DEFAULT_FPS):  # pragma: no cover
    """Run the curses capture loop, rendering each cell with `draw`.

    Args:
        draw: callback `draw(stdscr, x, y, blue, green, red)` for a single cell.
        device: webcam index, or None to select interactively.
        setup: optional `setup(stdscr)` run once after curses initialization.
        cell_aspect: terminal cell height/width ratio, or None to measure it.
        fps: target frames per second, used to throttle the render loop.

    The loop exits when ESC or Ctrl+C is pressed.
    """
    device = select_device(device)
    aspect = cell_aspect if cell_aspect is not None else cell_aspect_ratio()

    with contextlib.suppress(AttributeError):
        cv2.utils.logging.setLogLevel(cv2.utils.logging.LOG_LEVEL_SILENT)

    with suppressed_stderr():
        capture = cv2.VideoCapture(device)

    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.timeout(frame_interval(fps))

    with contextlib.suppress(curses.error):
        curses.curs_set(0)

    try:
        if setup is not None:
            setup(stdscr)

        rows, columns = terminal_size()
        height, width, top, left = square_extent(rows, columns, aspect)

        while True:
            if stdscr.getch() == ESCAPE_KEY:
                break

            frame = capture.read()[1]
            if frame is None:
                continue

            thumbnail = cv2.resize(crop_square(frame), (width, height))

            stdscr.erase()
            for x, y, blue, green, red in iter_cells(thumbnail):
                try:
                    draw(stdscr, top + x, left + y, blue, green, red)
                except curses.error:
                    pass

            stdscr.refresh()
    finally:
        curses.nocbreak()
        curses.endwin()
        capture.release()
