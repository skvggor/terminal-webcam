import capture


class FakeScreen:
    def __init__(self):
        self.moves = []
        self.chars = []

    def move(self, x, y):
        self.moves.append((x, y))

    def addch(self, character):
        self.chars.append(character)


def test_draw_moves_and_writes_character():
    screen = FakeScreen()

    capture.draw(screen, 2, 3, 0, 0, 0)

    assert screen.moves == [(2, 3)]
    assert screen.chars == [' ']
