import curses

import color


class FakeScreen:
    def __init__(self):
        self.moves = []
        self.attrs = []
        self.chars = []

    def move(self, x, y):
        self.moves.append((x, y))

    def attrset(self, attr):
        self.attrs.append(attr)

    def addch(self, character):
        self.chars.append(character)


def test_draw_sets_color_pair_and_writes_character(monkeypatch):
    monkeypatch.setattr(curses, 'color_pair', lambda pair: pair)
    screen = FakeScreen()

    color.draw(screen, 1, 1, 0, 0, 0)

    assert screen.moves == [(1, 1)]
    assert screen.attrs == [1]
    assert screen.chars == [' ']


def test_initialize_colors_creates_depth_cubed_pairs(monkeypatch):
    created_colors = []
    created_pairs = []
    monkeypatch.setattr(curses, 'init_color', lambda *args: created_colors.append(args))
    monkeypatch.setattr(curses, 'init_pair', lambda *args: created_pairs.append(args))

    color.initialize_colors(2)

    assert len(created_colors) == 2**3
    assert len(created_pairs) == 2**3


def test_setup_starts_color_and_initializes_pairs(monkeypatch):
    calls = []
    monkeypatch.setattr(curses, 'start_color', lambda: calls.append('start'))
    monkeypatch.setattr(color, 'initialize_colors', lambda depth: calls.append(depth))

    color.setup(object())

    assert calls == ['start', color.COLOR_DEPTH]
