"""Pygame front end.  Click a tile or use arrow keys.
R = reshuffle, H = hint (one move), S = auto-solve, 3/4 = board size."""
import argparse
import time

import pygame

import puzzle

TILE, GAP, TOP = 110, 8, 90
BG, TILE_C, TEXT_C, ACCENT = (24, 26, 33), (58, 110, 165), (240, 240, 240), (255, 196, 0)


class Game:
    def __init__(self, n=3, seed=None):
        self.n = n
        self.rng = __import__("random").Random(seed)
        self.new()

    def new(self):
        self.state = puzzle.shuffle(self.n, 40 if self.n == 4 else 80, self.rng)
        self.moves, self.start, self.solution, self.msg = 0, time.time(), [], ""

    def slide(self, target_index):
        z = self.state.index(0)
        zr, zc = divmod(z, self.n)
        tr, tc = divmod(target_index, self.n)
        if abs(zr - tr) + abs(zc - tc) == 1:
            s = list(self.state)
            s[z], s[target_index] = s[target_index], s[z]
            self.state, self.moves = tuple(s), self.moves + 1
            return True
        return False

    def solve_path(self):
        # ponytail: weighted A* on 4x4 keeps hints instant but not always optimal
        path, _ = puzzle.astar(self.state, self.n, weight=1.0 if self.n == 3 else 1.6)
        return path[1:]

    def solved(self):
        return self.state == puzzle.goal(self.n)

    def draw(self, screen, font, small):
        screen.fill(BG)
        elapsed = int(time.time() - self.start)
        screen.blit(small.render(f"Moves: {self.moves}", True, TEXT_C), (GAP * 2, 20))
        screen.blit(small.render(f"Time: {elapsed}s", True, TEXT_C), (GAP * 2, 50))
        hint = "R shuffle  H hint  S solve  3/4 size"
        screen.blit(small.render(hint, True, (150, 150, 160)), (170, 35))
        for i, t in enumerate(self.state):
            if not t:
                continue
            r, c = divmod(i, self.n)
            rect = pygame.Rect(left(self.n) + c * (TILE + GAP), TOP + r * (TILE + GAP), TILE, TILE)
            color = ACCENT if t == i + 1 else TILE_C
            pygame.draw.rect(screen, color, rect, border_radius=12)
            label = font.render(str(t), True, BG if t == i + 1 else TEXT_C)
            screen.blit(label, label.get_rect(center=rect.center))
        if self.msg:
            text = font.render(self.msg, True, ACCENT)
            screen.blit(text, text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 40)))


def size_for(n):
    return max(GAP + n * (TILE + GAP), 520), TOP + n * (TILE + GAP) + 80


def left(n):
    """x offset that centers the board in the window"""
    return (size_for(n)[0] - n * (TILE + GAP) - GAP) // 2 + GAP


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", type=int, default=3, choices=(3, 4))
    ap.add_argument("--seed", type=int)
    ap.add_argument("--screenshot", help="render one frame to this PNG and exit")
    ap.add_argument("--play-moves", type=int, default=0, help="with --screenshot: apply N solver moves first")
    args = ap.parse_args()

    pygame.init()
    game = Game(args.size, args.seed)
    screen = pygame.display.set_mode(size_for(game.n))
    pygame.display.set_caption("Sliding Puzzle")
    font, small = pygame.font.SysFont(None, 56), pygame.font.SysFont(None, 28)

    if args.screenshot:
        for s in game.solve_path()[: args.play_moves]:
            game.state, game.moves = s, game.moves + 1
        if game.solved():
            game.msg = f"Solved in {game.moves} moves!"
        game.draw(screen, font, small)
        pygame.image.save(screen, args.screenshot)
        return

    clock = pygame.time.Clock()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return
            if e.type == pygame.MOUSEBUTTONDOWN and not game.solution:
                x, y = e.pos
                c, r = (x - left(game.n)) // (TILE + GAP), (y - TOP) // (TILE + GAP)
                if x >= left(game.n) and 0 <= r < game.n and 0 <= c < game.n:
                    game.slide(r * game.n + c)
            if e.type == pygame.KEYDOWN:
                z = game.state.index(0)
                # arrow = direction the tile moves, so the blank moves the opposite way
                delta = {pygame.K_UP: game.n, pygame.K_DOWN: -game.n, pygame.K_LEFT: 1, pygame.K_RIGHT: -1}
                if e.key in delta and 0 <= z + delta[e.key] < game.n ** 2:
                    game.slide(z + delta[e.key])
                elif e.key == pygame.K_r:
                    game.new()
                elif e.key == pygame.K_h and not game.solved():
                    game.state, game.moves = game.solve_path()[0], game.moves + 1
                elif e.key == pygame.K_s:
                    game.solution = game.solve_path()
                elif e.key in (pygame.K_3, pygame.K_4):
                    game = Game(3 if e.key == pygame.K_3 else 4)
                    screen = pygame.display.set_mode(size_for(game.n))
        if game.solution:
            game.state, game.moves = game.solution.pop(0), game.moves + 1
            pygame.time.wait(120)
        game.msg = f"Solved in {game.moves} moves!" if game.solved() else ""
        game.draw(screen, font, small)
        pygame.display.flip()
        clock.tick(30)


if __name__ == "__main__":
    main()
