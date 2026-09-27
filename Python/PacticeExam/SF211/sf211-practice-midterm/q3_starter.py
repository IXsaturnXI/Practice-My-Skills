"""
Q3 STARTER — one class, two control schemes, selected by a "control" string.

WARNING: this file contains THREE deliberate behavioural bugs on top of its
design smells. Find them before you refactor:
  1. diagonal movement is ~1.41x faster than straight movement
  2. the chaser oscillates around its target instead of settling
  3. the keyboard ball can be driven off-screen forever

    python q3_starter.py        (WASD or arrow keys)
"""

import pygame

from config import WIDTH, HEIGHT, FPS, BACKGROUND


class Ball:
    def __init__(self, control, center_x, center_y, radius, speed, color,
                 target=None):
        self._control = control      # "keyboard" or "ai"
        self._target = target        # used only when control == "ai"
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

    def move(self):
        if self._control == "keyboard":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self._center_x -= self._speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self._center_x += self._speed
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self._center_y -= self._speed
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self._center_y += self._speed
        elif self._control == "ai":
            if self._target._center_x > self._center_x:
                self._center_x += self._speed
            elif self._target._center_x < self._center_x:
                self._center_x -= self._speed
            if self._target._center_y > self._center_y:
                self._center_y += self._speed
            elif self._target._center_y < self._center_y:
                self._center_y -= self._speed

    def draw(self, screen):
        pygame.draw.circle(screen, self._color,
                           (int(self._center_x), int(self._center_y)),
                           self._radius)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Q3 STARTER — control-flag Ball (WASD/arrows)")
    clock = pygame.time.Clock()

    player = Ball("keyboard", WIDTH / 2, HEIGHT / 2, 20, 5, "white")
    enemy = Ball("ai", 40, 40, 14, 3, "red", target=player)
    balls = [player, enemy]

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