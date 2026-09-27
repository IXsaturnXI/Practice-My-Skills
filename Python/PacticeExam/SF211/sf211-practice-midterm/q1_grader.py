"""
SF211 — Pygame OOP Refactoring Exam
Autograder for Question 1 (q1.py): BouncingBall class

Usage:
    # Run standalone grader (grades q1.py by default):
    python q1_grader.py

    # Grade a specific target (e.g. reference solution):
    python q1_grader.py q1_solution.py
    python q1_grader.py --target q1_solution

    # Or run via pytest:
    pytest -v q1_grader.py
    GRADER_TARGET=q1_solution pytest -v q1_grader.py
"""

import argparse
import importlib
import inspect
import math
import os
import sys
import traceback
import pygame
import pytest

from ball_base import Ball
from config import WIDTH, HEIGHT, random_color


def get_target_name() -> str:
    target = os.environ.get("GRADER_TARGET", "q1").strip()
    if target.endswith(".py"):
        target = target[:-3]
    return target


def get_bouncing_ball_class():
    target_name = get_target_name()
    try:
        mod = importlib.import_module(target_name)
    except Exception as err:
        pytest.fail(f"Failed to import target module '{target_name}': {err}")

    cls = getattr(mod, "BouncingBall", None)
    if cls is None:
        pytest.fail(f"Class 'BouncingBall' is not defined in '{target_name}'")
    return cls


def get_dx(ball):
    """Retrieve velocity in x direction, supporting both _dx attribute and dx property."""
    if hasattr(ball, "_dx"):
        return ball._dx
    if hasattr(ball, "dx"):
        return ball.dx
    return None


def get_dy(ball):
    """Retrieve velocity in y direction, supporting both _dy attribute and dy property."""
    if hasattr(ball, "_dy"):
        return ball._dy
    if hasattr(ball, "dy"):
        return ball.dy
    return None


def set_vel(ball, dx, dy):
    """Set ball velocity for testing boundary interactions."""
    if hasattr(ball, "_dx"):
        ball._dx = dx
    elif hasattr(ball, "dx"):
        try:
            setattr(ball, "dx", dx)
        except AttributeError:
            pass

    if hasattr(ball, "_dy"):
        ball._dy = dy
    elif hasattr(ball, "dy"):
        try:
            setattr(ball, "dy", dy)
        except AttributeError:
            pass


def set_pos(ball, x, y):
    """Set ball center position for testing boundary interactions."""
    if hasattr(ball, "_center_x"):
        ball._center_x = x
    elif hasattr(ball, "center_x"):
        try:
            setattr(ball, "center_x", x)
        except AttributeError:
            pass

    if hasattr(ball, "_center_y"):
        ball._center_y = y
    elif hasattr(ball, "center_y"):
        try:
            setattr(ball, "center_y", y)
        except AttributeError:
            pass


# ====================================================================
# Test Suite (Rubric: 100 Points Total)
# ====================================================================

def test_class_definition_and_inheritance():
    """Verify BouncingBall is defined, is a class, and inherits from Ball (10 pts)."""
    BouncingBall = get_bouncing_ball_class()
    assert inspect.isclass(BouncingBall), "BouncingBall must be a class."
    assert issubclass(BouncingBall, Ball), "BouncingBall must inherit from ball_base.Ball."
    assert hasattr(BouncingBall, "draw"), "BouncingBall must have a 'draw' method."
    assert callable(getattr(BouncingBall, "draw")), "'draw' must be a callable method."


def test_constructor_parameters_and_attributes():
    """Verify constructor parameters, absence of color parameter, and attribute setup (10 pts)."""
    BouncingBall = get_bouncing_ball_class()

    # Check constructor signature: (center_x, center_y, radius, speed)
    sig = inspect.signature(BouncingBall.__init__)
    params = list(sig.parameters.keys())[1:]  # skip 'self'
    assert len(params) == 4, (
        f"__init__ should take 4 parameters (center_x, center_y, radius, speed), got: {params}"
    )
    assert "color" not in params, (
        "BouncingBall.__init__ must not take a 'color' parameter; color must be randomized internally."
    )

    ball = BouncingBall(400, 300, radius=20, speed=5)
    assert ball.center_x == 400, f"Expected center_x == 400, got {ball.center_x}"
    assert ball.center_y == 300, f"Expected center_y == 300, got {ball.center_y}"
    assert ball.radius == 20, f"Expected radius == 20, got {ball.radius}"
    assert ball.speed == 5, f"Expected speed == 5, got {ball.speed}"

    # Encapsulation checks: internal attributes from Ball and BouncingBall
    for attr in ("_center_x", "_center_y", "_radius", "_speed", "_color", "_dx", "_dy"):
        assert hasattr(ball, attr), f"BouncingBall instance must have internal attribute '{attr}'."


def test_random_initialization():
    """Verify that initial color and direction are properly randomized across instances (10 pts)."""
    BouncingBall = get_bouncing_ball_class()

    balls = [BouncingBall(400, 300, 20, 5) for _ in range(12)]

    # Validate RGB color format
    for b in balls:
        assert isinstance(b.color, (tuple, list)) and len(b.color) == 3, (
            f"Ball color must be an RGB 3-tuple, got {b.color}"
        )
        for c in b.color:
            assert isinstance(c, int) and 0 <= c <= 255, (
                f"Color component must be an integer between 0 and 255, got {c} in {b.color}"
            )

    # Validate color randomization
    colors = set(tuple(b.color) for b in balls)
    assert len(colors) > 1, "Ball colors must be randomized; all instances had identical colors."

    # Validate direction randomization
    directions = set((round(get_dx(b), 4), round(get_dy(b), 4)) for b in balls)
    assert len(directions) > 1, "Ball initial velocities must be randomized."


def test_velocity_attributes_and_magnitude():
    """Verify velocity attributes (_dx, _dy) exist and hypot matches speed (10 pts)."""
    BouncingBall = get_bouncing_ball_class()

    for spd in (1, 4, 7.5, 15):
        ball = BouncingBall(400, 300, radius=20, speed=spd)
        dx = get_dx(ball)
        dy = get_dy(ball)
        assert dx is not None, "BouncingBall must store velocity in '_dx' (or property 'dx')."
        assert dy is not None, "BouncingBall must store velocity in '_dy' (or property 'dy')."

        mag = math.hypot(dx, dy)
        assert math.isclose(mag, spd, rel_tol=1e-6), (
            f"Velocity magnitude sqrt(dx^2 + dy^2) = {mag} does not match speed = {spd}."
        )


def test_open_space_movement():
    """Verify movement in open space updates position by (dx, dy) and preserves color (10 pts)."""
    BouncingBall = get_bouncing_ball_class()

    ball = BouncingBall(400, 300, radius=20, speed=5)
    x0, y0 = ball.center_x, ball.center_y
    dx0, dy0 = get_dx(ball), get_dy(ball)
    assert dx0 is not None and dy0 is not None, "Velocity components must not be None."
    color0 = ball.color

    ball.move()

    assert math.isclose(ball.center_x, x0 + dx0, rel_tol=1e-6), (
        f"center_x after move ({ball.center_x}) should be {x0 + dx0}."
    )
    assert math.isclose(ball.center_y, y0 + dy0, rel_tol=1e-6), (
        f"center_y after move ({ball.center_y}) should be {y0 + dy0}."
    )
    assert ball.color == color0, (
        "Ball color should not change during normal movement without hitting a wall."
    )


def test_window_containment_and_clamping():
    """Verify ball never leaves window bounds across 3000 frames at high speed (10 pts)."""
    BouncingBall = get_bouncing_ball_class()

    ball = BouncingBall(400, 300, radius=20, speed=17)
    for frame in range(3000):
        ball.move()
        assert ball.radius <= ball.center_x <= WIDTH - ball.radius, (
            f"Frame {frame}: ball horizontally out of bounds: center_x={ball.center_x}, radius={ball.radius}"
        )
        assert ball.radius <= ball.center_y <= HEIGHT - ball.radius, (
            f"Frame {frame}: ball vertically out of bounds: center_y={ball.center_y}, radius={ball.radius}"
        )


def test_wall_bounce_reflection():
    """Verify reflection and clamping off all four window boundaries (15 pts)."""
    BouncingBall = get_bouncing_ball_class()

    # 1. Left Wall (x - r <= 0)
    b_left = BouncingBall(100, 300, radius=20, speed=5)
    set_pos(b_left, 22, 300)
    set_vel(b_left, -5, 0)
    b_left.move()
    assert math.isclose(b_left.center_x, b_left.radius, abs_tol=1e-5), (
        f"Left wall: ball should be clamped to x = radius ({b_left.radius}), got {b_left.center_x}."
    )
    assert get_dx(b_left) > 0, f"Left wall: dx should be positive after bounce, got {get_dx(b_left)}."

    # 2. Right Wall (x + r >= WIDTH)
    b_right = BouncingBall(100, 300, radius=20, speed=5)
    set_pos(b_right, WIDTH - 22, 300)
    set_vel(b_right, 5, 0)
    b_right.move()
    assert math.isclose(b_right.center_x, WIDTH - b_right.radius, abs_tol=1e-5), (
        f"Right wall: ball should be clamped to x = WIDTH - radius ({WIDTH - b_right.radius}), got {b_right.center_x}."
    )
    assert get_dx(b_right) < 0, f"Right wall: dx should be negative after bounce, got {get_dx(b_right)}."

    # 3. Top Wall (y - r <= 0)
    b_top = BouncingBall(400, 100, radius=20, speed=5)
    set_pos(b_top, 400, 22)
    set_vel(b_top, 0, -5)
    b_top.move()
    assert math.isclose(b_top.center_y, b_top.radius, abs_tol=1e-5), (
        f"Top wall: ball should be clamped to y = radius ({b_top.radius}), got {b_top.center_y}."
    )
    assert get_dy(b_top) > 0, f"Top wall: dy should be positive after bounce, got {get_dy(b_top)}."

    # 4. Bottom Wall (y + r >= HEIGHT)
    b_bottom = BouncingBall(400, 100, radius=20, speed=5)
    set_pos(b_bottom, 400, HEIGHT - 22)
    set_vel(b_bottom, 0, 5)
    b_bottom.move()
    assert math.isclose(b_bottom.center_y, HEIGHT - b_bottom.radius, abs_tol=1e-5), (
        f"Bottom wall: ball should be clamped to y = HEIGHT - radius ({HEIGHT - b_bottom.radius}), got {b_bottom.center_y}."
    )
    assert get_dy(b_bottom) < 0, f"Bottom wall: dy should be negative after bounce, got {get_dy(b_bottom)}."


def test_no_jitter_bug():
    """Verify velocity sign is idempotent and does not oscillate every frame (10 pts)."""
    BouncingBall = get_bouncing_ball_class()

    ball = BouncingBall(WIDTH - 22, 300, radius=20, speed=5)
    for _ in range(200):
        ball.move()
        dx = get_dx(ball)
        if dx is not None and dx < 0:
            break

    signs = []
    positions = []
    for _ in range(5):
        prev_x = ball.center_x
        ball.move()
        dx = get_dx(ball)
        if dx is not None:
            signs.append(dx < 0)
        positions.append(ball.center_x < prev_x)

    if signs:
        assert all(signs), (
            "Velocity flipped sign every frame (jitter bug): sign was not set idempotently using abs()/-abs()."
        )
    assert all(positions), (
        "Ball position oscillated direction on wall (jitter bug): movement was not consistently away from wall."
    )


def test_color_changes_on_wall_hit():
    """Verify ball recolors upon wall collision and corner hits (10 pts)."""
    BouncingBall = get_bouncing_ball_class()

    ball = BouncingBall(400, 300, radius=20, speed=9)
    initial_color = ball.color
    changed = False
    for _ in range(500):
        ball.move()
        if ball.color != initial_color:
            changed = True
            break
    assert changed, "Ball color never changed after hitting a wall."

    # Test corner collision
    corner_ball = BouncingBall(21, 21, radius=20, speed=5)
    set_pos(corner_ball, 21, 21)
    set_vel(corner_ball, -5, -5)
    corner_color = corner_ball.color
    corner_ball.move()
    assert math.isclose(corner_ball.center_x, corner_ball.radius, abs_tol=1e-5)
    assert math.isclose(corner_ball.center_y, corner_ball.radius, abs_tol=1e-5)
    assert get_dx(corner_ball) > 0 and get_dy(corner_ball) > 0
    assert corner_ball.color != corner_color or isinstance(corner_ball.color, (tuple, list))


def test_draw_method_renders_circle():
    """Verify inherited draw method draws correctly to a Pygame Surface (5 pts)."""
    BouncingBall = get_bouncing_ball_class()

    ball = BouncingBall(400, 300, radius=20, speed=5)
    surface = pygame.Surface((WIDTH, HEIGHT))
    surface.fill((0, 0, 0))

    ball.draw(surface)

    # Pixel at ball center should be colored with ball.color
    drawn_color = surface.get_at((int(ball.center_x), int(ball.center_y)))[:3]
    assert drawn_color == tuple(ball.color), (
        f"Drawn pixel color {drawn_color} at center does not match ball color {ball.color}."
    )


# ====================================================================
# Rubric Definition & Standalone Grader Runner
# ====================================================================

RUBRIC = [
    (test_class_definition_and_inheritance, 10, "BouncingBall class definition and inheritance from Ball"),
    (test_constructor_parameters_and_attributes, 10, "Constructor signature, encapsulation, and parameter check"),
    (test_random_initialization, 10, "Randomization of initial color and velocity direction"),
    (test_velocity_attributes_and_magnitude, 10, "Velocity (_dx, _dy) encapsulation and magnitude matching speed"),
    (test_open_space_movement, 10, "Accurate movement in open space without color mutation"),
    (test_window_containment_and_clamping, 10, "Ball strictly contained within screen boundaries"),
    (test_wall_bounce_reflection, 15, "Proper reflection and clamping on all 4 walls"),
    (test_no_jitter_bug, 10, "Idempotent bounce behavior preventing jitter bug"),
    (test_color_changes_on_wall_hit, 10, "Color changes upon wall collision & corner bounce"),
    (test_draw_method_renders_circle, 5, "Inherited draw() renders circle on Pygame Surface"),
]


def run_grader(target: str = "q1", verbose: bool = False):
    os.environ["GRADER_TARGET"] = target

    sep_width = 72
    print("=" * sep_width)
    print(f" SF211 OOP Exam — Q1 Autograder (BouncingBall)")
    print(f" Target module: {target}.py")
    print("=" * sep_width)

    total_score = 0
    max_score = sum(pts for _, pts, _ in RUBRIC)
    failed_tests = []

    for test_fn, pts, desc in RUBRIC:
        name = test_fn.__name__
        try:
            test_fn()
            total_score += pts
            print(f" [PASS] {pts:2d}/{pts:2d}  {name}")
            print(f"               {desc}")
        except BaseException as exc:
            # Handle KeyboardInterrupt / SystemExit cleanly
            if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                raise
            err_msg = str(exc)
            if not err_msg and hasattr(exc, "msg"):
                err_msg = str(exc.msg)
            print(f" [FAIL]  0/{pts:2d}  {name}")
            print(f"               {desc}")
            print(f"               -> ERROR: {err_msg}")
            failed_tests.append((name, desc, err_msg, traceback.format_exc()))

    print("-" * sep_width)
    pct = (total_score / max_score) * 100
    print(f" Total Score: {total_score} / {max_score} ({pct:.1f}%)")

    if failed_tests:
        print(f" Status: FAILED ({len(failed_tests)} of {len(RUBRIC)} tests failed)")
        if verbose:
            print("\nDetailed Failure Tracebacks:")
            print("-" * sep_width)
            for name, desc, err_msg, tb in failed_tests:
                print(f"=== {name} ===")
                print(tb)
        print("=" * sep_width)
        return 1
    else:
        print(" Status: PASSED ALL CHECKS (Perfect Score!)")
        print("=" * sep_width)
        return 0


def main():
    parser = argparse.ArgumentParser(description="SF211 Exam Q1 Grader for BouncingBall")
    parser.add_argument(
        "target_pos",
        nargs="?",
        default=None,
        help="Optional positional target module to grade (default: q1)",
    )
    parser.add_argument(
        "--target",
        "-t",
        default=None,
        help="Target module to grade (e.g., q1, q1_solution)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print verbose tracebacks for failed tests",
    )
    args = parser.parse_args()

    target = args.target or args.target_pos or "q1"
    if target.endswith(".py"):
        target = target[:-3]

    exit_code = run_grader(target=target, verbose=args.verbose)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
