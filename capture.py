"""Capture webcam frames and render them as monochrome ASCII art in the terminal."""

import curses
import os
import signal
import sys

import cv2

from ascii_art import iter_cells, palette_character


def signal_handler(sig, _):  # pragma: no cover
    """Handle Ctrl+C and clean up curses before exiting."""
    print('You pressed Ctrl + C!')
    curses.endwin()
    sys.exit(0)


def main():  # pragma: no cover
    """Capture images from the webcam and display them in the terminal."""
    stdscr = curses.initscr()
    signal.signal(signal.SIGINT, signal_handler)
    capture = cv2.VideoCapture(0)
    rows, columns = map(int, os.popen('stty size', 'r').read().split())

    while True:
        frame = capture.read()[1]
        thumbnail = cv2.resize(frame, (columns, rows))

        for x, y, blue, green, red in iter_cells(thumbnail):
            try:
                stdscr.move(x, y)
                stdscr.addch(palette_character(blue, green, red))
            except curses.error:
                pass

        stdscr.refresh()


if __name__ == '__main__':
    main()
