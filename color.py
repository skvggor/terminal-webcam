"""Capture webcam frames and render them as colored ASCII art in the terminal."""

import curses
import os
import signal
import sys

import cv2

from ascii_art import color_pair, iter_cells, palette_character

COLOR_DEPTH = 6


def signal_handler(sig, _):  # pragma: no cover
    """Handle Ctrl+C and clean up curses before exiting."""
    print('You pressed Ctrl + C!')
    curses.endwin()
    sys.exit(0)


def initialize_colors(depth):  # pragma: no cover
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


def main():  # pragma: no cover
    """Capture images from the webcam and display them in the terminal."""
    stdscr = curses.initscr()
    curses.start_color()
    signal.signal(signal.SIGINT, signal_handler)
    capture = cv2.VideoCapture(0)
    rows, columns = map(int, os.popen('stty size', 'r').read().split())

    initialize_colors(COLOR_DEPTH)

    while True:
        frame = capture.read()[1]
        thumbnail = cv2.resize(frame, (columns, rows))

        for x, y, blue, green, red in iter_cells(thumbnail):
            try:
                stdscr.move(x, y)
                stdscr.attrset(curses.color_pair(color_pair(blue, green, red, COLOR_DEPTH)))
                stdscr.addch(palette_character(blue, green, red))
            except curses.error:
                pass

        stdscr.refresh()


if __name__ == '__main__':
    main()
