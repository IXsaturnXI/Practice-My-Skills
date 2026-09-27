"""
Q4 STARTER — skeleton only. Fill in the TODOs.

Constraint: the update and draw loops must contain NO isinstance() call and
NO branching on object type.
"""

import pygame

from config import WIDTH, HEIGHT, FPS, BACKGROUND


def build_scene():
    """Return a single list containing every object in the scene.

    TODO: 3 x BouncingBall (Q1)
    TODO: 1 x CircularBall + 1 x HorizontalBall (Q2)
    TODO: 1 x keyboard-controlled ball + 1 x ball chasing it (Q3)

    Hint: Q1/Q2 balls inherit from Ball; Q3 balls COMPOSE a Controller.
    Part (b) asks you to reconcile the two designs first.
    """
    balls = []
    return balls


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Q4 STARTER")
    clock = pygame.time.Clock()

    balls = build_scene()

    running = True
    while running:
        for event in pygame.event.get():        # 1. events
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BACKGROUND)   
        # TODO 2. update — one uniform loop
        # TODO 3. draw   — one uniform loop

        pygame.display.flip()                   # 4. present
        clock.tick(FPS)                         # 5. control time

    pygame.quit()


if __name__ == "__main__":
    main()