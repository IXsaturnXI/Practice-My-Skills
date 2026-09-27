import math

import pygame

from ball_base import Ball
from config import WIDTH, HEIGHT, FPS, BACKGROUND


#TODO: implement CircularBall and HorizontalBall classes that inherit from ball_base.Ball.


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Q2 — polymorphic motion")
    clock = pygame.time.Clock()

    # TODO: create a list of CircularBall and HorizontalBall instances.
    balls = [ ]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        for ball in balls:          # no isinstance, no type test
            ball.move()

        screen.fill(BACKGROUND)
        for ball in balls:
            ball.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()