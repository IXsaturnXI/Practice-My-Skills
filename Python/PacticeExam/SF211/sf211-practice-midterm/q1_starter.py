"""
Q1 STARTER — procedural, global state, parallel dictionaries.

This program WORKS. Run it, watch it, then refactor it into a
BouncingBall class that inherits from ball_base.Ball.

    python q1_starter.py
"""

import math
import random

import pygame

from config import WIDTH, HEIGHT, FPS, BACKGROUND

# ---------------------------------------------------------------- #
# SMELL: global mutable state, shared by every function below.
# ---------------------------------------------------------------- #
balls = []


def random_color():
    return (random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255))


def create_ball(cx, cy, r, speed):
    global balls
    angle = random.uniform(0, 2 * math.pi)
    balls.append({"x": cx, "y": cy, "r": r, "speed": speed,
                  "dx": speed * math.cos(angle),
                  "dy": speed * math.sin(angle),
                  "color": random_color()})


def update_balls():
    global balls
    for b in balls:
        b["x"] += b["dx"]
        b["y"] += b["dy"]
        hit = False
        if b["x"] - b["r"] <= 0:
            b["x"] = b["r"];          b["dx"] = abs(b["dx"]);   hit = True
        elif b["x"] + b["r"] >= WIDTH:
            b["x"] = WIDTH - b["r"];  b["dx"] = -abs(b["dx"]);  hit = True
        if b["y"] - b["r"] <= 0:
            b["y"] = b["r"];          b["dy"] = abs(b["dy"]);   hit = True
        elif b["y"] + b["r"] >= HEIGHT:
            b["y"] = HEIGHT - b["r"]; b["dy"] = -abs(b["dy"]);  hit = True
        if hit:
            b["color"] = random_color()


def draw_balls(screen):
    global balls
    for b in balls:
        pygame.draw.circle(screen, b["color"],
                           (int(b["x"]), int(b["y"])), b["r"])


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Q1 STARTER — procedural bouncing balls")
    clock = pygame.time.Clock()

    for _ in range(3):
        create_ball(random.randint(100, 700),
                    random.randint(100, 500), 18, 5)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        update_balls()

        screen.fill(BACKGROUND)
        draw_balls(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()