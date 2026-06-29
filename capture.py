"""Render the webcam as monochrome ASCII art in the terminal."""

import argparse

from ascii_art import palette_character
from webcam import run


def draw(stdscr, x, y, blue, green, red):
    """Render a single cell as a monochrome ASCII character."""
    stdscr.move(x, y)
    stdscr.addch(palette_character(blue, green, red))


def main():  # pragma: no cover
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-d', '--device', type=int, default=None, help='Webcam device index')
    args = parser.parse_args()
    run(draw, device=args.device)


if __name__ == '__main__':
    main()
