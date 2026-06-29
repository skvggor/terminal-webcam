"""Render the webcam as monochrome ASCII art in the terminal."""

import argparse

from ascii_art import palette_character
from webcam import DEFAULT_FPS, print_devices, run


def draw(stdscr, x, y, blue, green, red):
    """Render a single cell as a monochrome ASCII character."""
    stdscr.move(x, y)
    stdscr.addch(palette_character(blue, green, red))


def main():  # pragma: no cover
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-d', '--device', type=int, default=None, help='Webcam device index')
    parser.add_argument(
        '-a',
        '--aspect',
        type=float,
        default=None,
        help='Terminal cell height/width ratio (auto-detected when omitted)',
    )
    parser.add_argument(
        '-f', '--fps', type=float, default=DEFAULT_FPS, help='Target frames per second'
    )
    parser.add_argument(
        '-l',
        '--list',
        action='store_true',
        help='List webcams and the detected aspect ratio, then exit',
    )
    args = parser.parse_args()
    if args.list:
        print_devices()
        return
    run(draw, device=args.device, cell_aspect=args.aspect, fps=args.fps)


if __name__ == '__main__':
    main()
