"""Compare how many nodes A* expands with each heuristic. Writes docs/heuristics.png."""
import random
import statistics

import matplotlib.pyplot as plt

import puzzle

rng = random.Random(7)
heuristics = {"No heuristic (BFS-like)": puzzle.zero, "Misplaced tiles": puzzle.misplaced, "Manhattan distance": puzzle.manhattan}
results = {name: {} for name in heuristics}

for _ in range(60):
    start = puzzle.shuffle(3, rng.randint(10, 60), rng)
    path, _ = puzzle.astar(start, 3)
    depth = len(path) - 1
    for name, h in heuristics.items():
        _, expanded = puzzle.astar(start, 3, h)
        results[name].setdefault(depth, []).append(expanded)

fig, ax = plt.subplots(figsize=(8, 4.5))
for name, by_depth in results.items():
    depths = sorted(by_depth)
    ax.plot(depths, [statistics.mean(by_depth[d]) for d in depths], marker="o", label=name)
ax.set_yscale("log")
ax.set_xlabel("Optimal solution length (moves)")
ax.set_ylabel("Nodes expanded (log scale)")
ax.set_title("A* on the 8-puzzle: a better heuristic searches far less")
ax.grid(alpha=0.3)
ax.legend()
fig.tight_layout()
fig.savefig("docs/heuristics.png", dpi=120)

for name, by_depth in results.items():
    allv = [v for vs in by_depth.values() for v in vs]
    print(f"{name:26s} mean nodes expanded: {statistics.mean(allv):>9,.0f}")
