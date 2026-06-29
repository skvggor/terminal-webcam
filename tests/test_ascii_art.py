import numpy
import pytest

from ascii_art import (
    PALETTE,
    color_pair,
    iter_cells,
    luminance,
    palette_character,
    palette_index,
)


def test_luminance_black_is_zero():
    assert luminance(0, 0, 0) == 0


def test_luminance_uses_rec601_weights():
    assert luminance(100, 200, 50) == pytest.approx(100 * 0.1145 + 200 * 0.5866 + 50 * 0.2989)


def test_palette_index_black_maps_to_first_character():
    assert palette_index(0) == 0


def test_palette_index_bright_maps_to_last_character():
    assert palette_index(255) == len(PALETTE) - 1


def test_palette_index_wraps_when_value_overflows():
    assert palette_index(256.0) == 0


def test_palette_character_black_is_space():
    assert palette_character(0, 0, 0) == ' '


def test_palette_character_white_is_densest():
    assert palette_character(255, 255, 255) == PALETTE[-1]


def test_color_pair_black_is_one():
    assert color_pair(0, 0, 0) == 1


def test_color_pair_white_is_max():
    depth = 6
    highest = depth - 1
    assert color_pair(255, 255, 255) == highest * depth * depth + highest * depth + highest + 1


def test_color_pair_honors_depth():
    assert color_pair(0, 0, 0, depth=4) == 1


def test_iter_cells_yields_every_pixel():
    frame = numpy.array([[[1, 2, 3], [4, 5, 6]]], dtype=numpy.uint8)
    cells = list(iter_cells(frame))

    assert len(cells) == 2
    assert cells[0] == (0, 0, 1, 2, 3)
    assert cells[1] == (0, 1, 4, 5, 6)
