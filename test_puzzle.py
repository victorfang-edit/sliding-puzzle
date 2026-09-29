import random

import puzzle


def test_goal_is_solvable():
    assert puzzle.is_solvable(puzzle.goal(3), 3)
    assert puzzle.is_solvable(puzzle.goal(4), 4)


def test_swapped_tiles_unsolvable():
    s = list(puzzle.goal(3))
    s[0], s[1] = s[1], s[0]
    assert not puzzle.is_solvable(tuple(s), 3)


def test_shuffle_always_solvable():
    rng = random.Random(1)
    for n in (3, 4):
        for _ in range(50):
            assert puzzle.is_solvable(puzzle.shuffle(n, 30, rng), n)


def test_astar_finds_optimal_path():
    start = (1, 2, 3, 4, 5, 6, 0, 7, 8)  # two moves from solved
    path, _ = puzzle.astar(start, 3)
    assert path[-1] == puzzle.goal(3) and len(path) - 1 == 2


def test_all_heuristics_agree_on_length():
    start = puzzle.shuffle(3, 40, random.Random(3))
    lengths = {len(puzzle.astar(start, 3, h)[0]) for h in (puzzle.zero, puzzle.misplaced, puzzle.manhattan)}
    assert len(lengths) == 1


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("all tests passed")
