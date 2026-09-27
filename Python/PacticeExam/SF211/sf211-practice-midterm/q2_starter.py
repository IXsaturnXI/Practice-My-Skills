"""
Q2 STARTER — one class, two behaviours, selected by a "kind" string.

Smells to find: type code + conditional dispatch, temporary fields,
duplicated draw() branches, optional-but-mandatory constructor args.

    python q2_starter.py
"""

import math

import pygame

from config import WIDTH, HEIGHT, FPS, BACKGROUND


class Ball:
    def __init__(self, kind, radius, speed, color,
                 orbit_radius=0, start_angle=0.0):
        self._kind = kind                    # "circular" or "horizontal"
        self._radius = radius
        self._speed = speed
        self._color = color
        self._orbit_radius = orbit_radius    # unused when horizontal
        self._angle = start_angle            # unused when horizontal
        self._orbit_center_x = WIDTH / 2     # unused when horizontal
        self._orbit_center_y = HEIGHT / 2    # unused when horizontal

        if kind == "circular":
            self._center_x = self._orbit_center_x + \
                orbit_radius * math.cos(start_angle)
            self._center_y = self._orbit_center_y + \
                orbit_radius * math.sin(start_angle)
        elif kind == "horizontal":
            self._center_x = -radius         # enters from the left wall
            self._center_y = HEIGHT / 2
        else:
            raise ValueError("unknown kind: " + kind)

    @property
    def center_x(self):
        return self._center_x

    @property
    def center_y(self):
        return self._center_y

    def move(self):
        if self._kind == "circular":
            self._angle += self._speed / self._orbit_radius
            self._angle %= 2 * math.pi
            self._center_x = self._orbit_center_x + \
                self._orbit_radius * math.cos(self._angle)
            self._center_y = self._orbit_center_y + \
                self._orbit_radius * math.sin(self._angle)
        elif self._kind == "horizontal":
            self._center_x += self._speed
            if self._center_x - self._radius > WIDTH:
                self._center_x = -self._radius

    def draw(self, screen):
        if self._kind == "circular":
            pygame.draw.circle(screen, self._color,
                               (int(self._center_x), int(self._center_y)),
                               self._radius)
        elif self._kind == "horizontal":
            pygame.draw.circle(screen, self._color,
                               (int(self._center_x), int(self._center_y)),
                               self._radius)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Q2 STARTER — type-code Ball")
    clock = pygame.time.Clock()

    balls = [
        Ball("circular", 12, 4, "cyan", orbit_radius=150),
        Ball("circular", 8, 4, "magenta", orbit_radius=80, start_angle=math.pi),
        Ball("horizontal", 25, 6, "yellow"),
    ]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        for ball in balls:
            ball.move()

        screen.fill(BACKGROUND)
        for ball in balls:
            ball.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()