"""Week 5: Pacman arena implementation WITHOUT inheritance.

This file demonstrates the "before inheritance" state shown in lecture:
Each entity class (Pacman, Ghost, Pellet) duplicates its own object infrastructure:
- position tracking (x, y, speed)
- Pygame image and rect management
- active status flag
- position synchronization (sync_position)
- rendering logic (draw)

Compare this file with `code/week05/exercise_solution.py` to see how a shared
`GameObject` base class removes duplication and centralizes shared infrastructure.
"""

import math
import pygame

# Window and Game Constants
WIDTH = 800
HEIGHT = 600
FPS = 60
BACKGROUND_COLOR = (20, 24, 40)
PACMAN_COLOR = (255, 238, 0)
GHOST_COLOR = (230, 40, 40)
PELLET_COLOR = (255, 183, 77)


# =============================================================================
# THREE INDEPENDENT CLASSES (NO INHERITANCE / REPEATED INFRASTRUCTURE)
# =============================================================================

class Pacman:
    """Player-controlled Pacman entity without a shared base class."""

    def __init__(self, x, y):
        # Duplicated infrastructure: position & speed
        self.x = float(x)
        self.y = float(y)
        self.speed = 5.0

        # Duplicated infrastructure: Pygame surface & rect hitbox
        self.image = pygame.Surface((36, 36))
        self.image.fill(PACMAN_COLOR)
        self.rect = self.image.get_rect(topleft=(round(x), round(y)))

        # Duplicated infrastructure: active state
        self.active = True

        # Pacman-specific state
        self.lives = 3
        self.score = 0
        self.facing_angle = 0.0
        self.mouth_phase = 0

    def sync_position(self):
        """Duplicated method: synchronize rect with float coordinates."""
        self.rect.topleft = (round(self.x), round(self.y))

    def update(self, bounds=None, controls=None):
        """Update position based on keyboard input and clamp within bounds."""
        if controls is None:
            return

        def is_pressed(key):
            if hasattr(controls, "get"):
                return controls.get(key, False)
            try:
                return bool(controls[key])
            except (IndexError, KeyError):
                return False

        dx = int(is_pressed(pygame.K_RIGHT) or is_pressed(pygame.K_d))
        dx -= int(is_pressed(pygame.K_LEFT) or is_pressed(pygame.K_a))
        dy = int(is_pressed(pygame.K_DOWN) or is_pressed(pygame.K_s))
        dy -= int(is_pressed(pygame.K_UP) or is_pressed(pygame.K_w))

        if dx or dy:
            self.facing_angle = math.atan2(dy, dx)
            self.mouth_phase += 1
        else:
            self.mouth_phase = 0

        self.x += dx * self.speed
        self.y += dy * self.speed
        self.sync_position()

        if bounds is not None:
            self.rect.clamp_ip(bounds)
            self.x, self.y = self.rect.topleft

    def draw(self, screen):
        """Draw Pacman as an animated chomping circle if active."""
        if not self.active:
            return

        if not hasattr(pygame, "draw"):
            screen.blit(self.image, self.rect)
            return

        center = self.rect.center
        radius = self.rect.width // 2
        mouth_open = 0.25 + 0.18 * abs(math.sin(self.mouth_phase * 0.35))
        upper_angle = self.facing_angle + mouth_open
        lower_angle = self.facing_angle - mouth_open
        mouth_tip = (
            center[0] + radius * math.cos(self.facing_angle),
            center[1] + radius * math.sin(self.facing_angle),
        )
        upper_point = (
            center[0] + radius * math.cos(upper_angle),
            center[1] + radius * math.sin(upper_angle),
        )
        lower_point = (
            center[0] + radius * math.cos(lower_angle),
            center[1] + radius * math.sin(lower_angle),
        )

        pygame.draw.circle(screen, PACMAN_COLOR, center, radius)
        pygame.draw.polygon(
            screen,
            BACKGROUND_COLOR,
            [center, upper_point, mouth_tip, lower_point],
        )


class Ghost:
    """Autonomous Ghost entity without a shared base class."""

    def __init__(self, x, y, patrol_left, patrol_right):
        # Duplicated infrastructure: position & speed
        self.x = float(x)
        self.y = float(y)
        self.speed = 3.0

        # Duplicated infrastructure: Pygame surface & rect hitbox
        self.image = pygame.Surface((36, 36))
        self.image.fill(GHOST_COLOR)
        self.rect = self.image.get_rect(topleft=(round(x), round(y)))

        # Duplicated infrastructure: active state
        self.active = True

        # Ghost-specific state
        self.patrol_left = patrol_left
        self.patrol_right = patrol_right

    def sync_position(self):
        """Duplicated method: synchronize rect with float coordinates."""
        self.rect.topleft = (round(self.x), round(self.y))

    def update(self, bounds=None, controls=None):
        """Patrol horizontally and bounce between patrol bounds."""
        self.x += self.speed

        if self.x <= self.patrol_left:
            self.x = self.patrol_left
            self.speed = abs(self.speed)
        elif self.x + self.rect.width >= self.patrol_right:
            self.x = self.patrol_right - self.rect.width
            self.speed = -abs(self.speed)

        self.sync_position()

    def draw(self, screen):
        """Draw the ghost as a rounded body with directional eyes if active."""
        if not self.active:
            return

        if not hasattr(pygame, "draw"):
            screen.blit(self.image, self.rect)
            return

        body = self.rect
        radius = body.width // 2
        center_x = body.centerx
        head_center = (center_x, body.y + radius)

        pygame.draw.circle(screen, GHOST_COLOR, head_center, radius)
        pygame.draw.rect(
            screen,
            GHOST_COLOR,
            (body.x, body.y + radius, body.width, body.height - radius),
        )

        wave_radius = body.width // 6
        wave_y = body.bottom - wave_radius
        for index in range(3):
            wave_x = body.x + wave_radius + index * wave_radius * 2
            pygame.draw.circle(
                screen,
                BACKGROUND_COLOR,
                (wave_x, wave_y),
                wave_radius,
            )

        eye_y = body.y + body.height // 3
        eye_offset = 7
        pupil_offset = 2 if self.speed >= 0 else -2
        for eye_x in (center_x - eye_offset, center_x + eye_offset):
            pygame.draw.circle(screen, "white", (eye_x, eye_y), 5)
            pygame.draw.circle(
                screen,
                (30, 60, 160),
                (eye_x + pupil_offset, eye_y),
                2,
            )


class Pellet:
    """Stationary score pellet entity without a shared base class."""

    def __init__(self, x, y, points=10):
        # Duplicated infrastructure: position & speed
        self.x = float(x)
        self.y = float(y)
        self.speed = 0.0

        # Duplicated infrastructure: Pygame surface & rect hitbox
        self.image = pygame.Surface((14, 14))
        self.image.fill(PELLET_COLOR)
        self.rect = self.image.get_rect(topleft=(round(x), round(y)))

        # Duplicated infrastructure: active state
        self.active = True

        # Pellet-specific state
        self.points = points

    def sync_position(self):
        """Duplicated method: synchronize rect with float coordinates."""
        self.rect.topleft = (round(self.x), round(self.y))

    def update(self, bounds=None, controls=None):
        """Stationary entity does not move on update."""
        pass

    def collect(self):
        """Deactivate the pellet and return its score value."""
        self.active = False
        return self.points

    def draw(self, screen):
        """Draw a pellet as a small glowing dot if active."""
        if not self.active:
            return

        if not hasattr(pygame, "draw"):
            screen.blit(self.image, self.rect)
            return

        center = self.rect.center
        outer_radius = self.rect.width // 2
        inner_radius = max(2, outer_radius - 3)
        pygame.draw.circle(screen, (255, 224, 130), center, outer_radius)
        pygame.draw.circle(screen, PELLET_COLOR, center, inner_radius)


# =============================================================================
# GAME LOOP HELPERS
# =============================================================================

def update_objects(objects, bounds=None, controls=None):
    """Update all game entities in the list."""
    for entity in objects:
        entity.update(bounds, controls)


def draw_objects(screen, objects):
    """Draw all active game entities in the list."""
    for entity in objects:
        entity.draw(screen)


# =============================================================================
# INTERACTIVE DEMONSTRATION ARENA
# =============================================================================

def main():
    pygame.init()
    pygame.display.set_caption("Week 5: Pacman Arena (Without Inheritance)")

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    bounds = screen.get_rect()
    clock = pygame.time.Clock()

    pacman = Pacman(100, 450)
    ghost = Ghost(250, 280, patrol_left=180, patrol_right=650)
    pellet = Pellet(600, 470, points=10)
    objects = [pacman, ghost, pellet]
    score = 0
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        controls = pygame.key.get_pressed()
        update_objects(objects, bounds, controls)

        if pacman.rect.colliderect(pellet.rect) and pellet.active:
            score += pellet.collect()
            pellet.x = 100 + (score * 37) % 650
            pellet.y = 140 + (score * 23) % 400
            pellet.active = True
            pellet.sync_position()

        screen.fill(BACKGROUND_COLOR)
        draw_objects(screen, objects)
        pygame.display.set_caption(
            f"Week 5 (No Inheritance) â€” Score: {score}"
            " | Arrow Keys/WASD: Move Pacman | Red: Ghost | Gold: Pellet"
        )
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()