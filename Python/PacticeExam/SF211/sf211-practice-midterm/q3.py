import math

import pygame

from config import WIDTH, HEIGHT, FPS, BACKGROUND

class Ball:
    """Owns appearance and drawing only. Movement is delegated."""

    def __init__(self, radius, color, controller):
        self._radius = radius
        self._color = color
        self._controller = controller
        # The controller is the single source of truth for position.
        self._center_x = controller.x
        self._center_y = controller.y

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
    def color(self):
        return self._color

    @property
    def controller(self):
        return self._controller

    @controller.setter
    def controller(self, new_controller):
        """Swapping behaviour at RUN TIME — impossible with subclassing."""
        self._controller = new_controller

    def draw(self, screen):
        pygame.draw.circle(screen, self._color,
                           (int(self._center_x), int(self._center_y)),
                           self._radius)

    def move(self):
        self._controller.move()                # 1. delegate
        self._center_x = self._controller.x    # 2. sync
        self._center_y = self._controller.y


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Q3 — composition (WASD/arrows)")
    clock = pygame.time.Clock()


    # TODO: create a few Ball instances with different controllers and add them to the `balls` list.
    balls = [ ]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        for ball in balls:          # identical treatment, no type test
            ball.move()

        screen.fill(BACKGROUND)
        for ball in balls:
            ball.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()