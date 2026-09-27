"""The Ball class GIVEN in the exam paper. Do not modify."""

import pygame


class Ball:
    def __init__(self, center_x, center_y, radius, speed, color):
        self._center_x = center_x
        self._center_y = center_y
        self._radius = radius
        self._speed = speed
        self._color = color

    @property
    def center_x(self):
        return self._center_x

    @property
    def center_y(self):
        return self._center_y

    @property
    def radius(self):
        return self._radius

    @property
    def speed(self):
        return self._speed

    @property
    def color(self):
        return self._color

    def draw(self, screen):
        pygame.draw.circle(screen, self._color,
                           (int(self._center_x), int(self._center_y)),
                           self._radius)

    def move(self):
        pass  # A plain Ball does not move. Subclasses decide how.