"""Shared constants and helpers for the SF211 OOP exam."""

import random

WIDTH, HEIGHT = 800, 600
FPS = 60

BACKGROUND = "black"


def random_color():
    """A random bright RGB colour (never too dark to see on black)."""
    return (random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255))