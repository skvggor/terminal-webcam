"""Render the webcam as colored ASCII art in the terminal."""

import argparse
import curses

from ascii_art import color_pair, palette_character
from webcam import run

COLOR_DEPTH = 6


def initialize_colors(depth):
    """Initialize curses color pairs for the given color depth."""
    splitby = (depth - 1) / 1000.0
    pair = 1

    for red in range(depth):
        for green in range(depth):
            for blue in range(depth):
                curses.init_color(
                    pair,
                    int(red / splitby),
                    int(green / splitby),
                    int(blue / splitby),
                )
                curses.init_pair(pair, pair, 0)
                pair += 1


def setup(stdscr):
    """Enable curses colors before the render loop starts."""
    curses.start_color()
    initialize_colors(COLOR_DEPTH)


def draw(stdscr, x, y, blue, green, red):
    """Render a single cell as a colored ASCII character."""
    stdscr.move(x, y)
    stdscr.attrset(curses.color_pair(color_pair(blue, green, red, COLOR_DEPTH)))
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
    args = parser.parse_args()
    run(draw, device=args.device, setup=setup, cell_aspect=args.aspect)


if __name__ == '__main__':
    main()
