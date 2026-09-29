"""Sliding-tile puzzle logic + A* solver. No pygame here so it's easy to test."""
import heapq
import random


def goal(n):
    return tuple(list(range(1, n * n)) + [0])


def neighbors(state, n):
    """Every state reachable by sliding one tile into the blank (0)."""
    z = state.index(0)
    r, c = divmod(z, n)
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        rr, cc = r + dr, c + dc
        if 0 <= rr < n and 0 <= cc < n:
            s = list(state)
            t = rr * n + cc
            s[z], s[t] = s[t], s[z]
            yield tuple(s)


def is_solvable(state, n):
    """Half of all tile arrangements can never be solved; inversion parity tells which."""
    tiles = [t for t in state if t]
    inv = sum(1 for i in range(len(tiles)) for j in range(i + 1, len(tiles)) if tiles[i] > tiles[j])
    if n % 2:
        return inv % 2 == 0
    blank_row_from_bottom = n - state.index(0) // n
    return (inv + blank_row_from_bottom) % 2 == 1


def shuffle(n, moves=80, rng=random):
    """Random walk from the goal, so the result is always solvable."""
    s, prev = goal(n), None
    for _ in range(moves):
        options = [x for x in neighbors(s, n) if x != prev]
        prev, s = s, rng.choice(options)
    return s


def zero(state, n):
    return 0


def misplaced(state, n):
    return sum(1 for i, t in enumerate(state) if t and t != i + 1)


def manhattan(state, n):
    d = 0
    for i, t in enumerate(state):
        if t:
            d += abs(i // n - (t - 1) // n) + abs(i % n - (t - 1) % n)
    return d


def astar(start, n, h=manhattan, weight=1.0):
    """Returns (path of states from start to goal, nodes expanded).
    weight > 1 trades optimality for speed (weighted A*)."""
    target = goal(n)
    frontier = [(weight * h(start, n), 0, start)]
    parent, cost, expanded = {start: None}, {start: 0}, 0
    while frontier:
        _, g, s = heapq.heappop(frontier)
        if s == target:
            break
        if g > cost[s]:
            continue  # stale heap entry
        expanded += 1
        for nb in neighbors(s, n):
            if nb not in cost or g + 1 < cost[nb]:
                cost[nb], parent[nb] = g + 1, s
                heapq.heappush(frontier, (g + 1 + weight * h(nb, n), g + 1, nb))
    path = []
    while s is not None:
        path.append(s)
        s = parent[s]
    return path[::-1], expanded
