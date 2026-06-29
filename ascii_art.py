"""Pure helpers for rendering webcam frames as terminal ASCII art."""

import math

PALETTE = [' ', '.', '.', '/', 'c', '(', '@', '#', '8']

RED_WEIGHT = 0.2989
GREEN_WEIGHT = 0.5866
BLUE_WEIGHT = 0.1145


def luminance(blue, green, red):
    """Return the perceived brightness of a BGR pixel using Rec. 601 weights."""
    return blue * BLUE_WEIGHT + green * GREEN_WEIGHT + red * RED_WEIGHT


def palette_index(value, palette=PALETTE):
    """Map a luminance value to an index in the palette."""
    return int(math.floor(value / (256.0 / len(palette)))) % len(palette)


def palette_character(blue, green, red, palette=PALETTE):
    """Return the ASCII character that represents a BGR pixel."""
    return palette[palette_index(luminance(blue, green, red), palette)]


def color_pair(blue, green, red, depth=6):
    """Return the curses color-pair number for a BGR pixel at the given color depth."""
    red_level = int(red / 256.0 * depth)
    green_level = int(green / 256.0 * depth)
    blue_level = int(blue / 256.0 * depth)
    return red_level * depth * depth + green_level * depth + blue_level + 1


def iter_cells(frame):
    """Yield (x, y, blue, green, red) for every pixel of a BGR frame."""
    for x in range(frame.shape[0]):
        for y in range(frame.shape[1]):
            blue, green, red = frame[x, y]
            yield x, y, blue, green, red
